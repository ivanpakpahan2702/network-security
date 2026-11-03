import re
import tempfile
import unittest
from pathlib import Path

from labcore.catalog import LABS
from labcore.curriculum import MODULES, MODULE_BY_ID
from labcore.dashboard import create_dashboard
from labcore.database import connect


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.app = create_dashboard(data_dir=self.root)
        self.app.testing = True
        self.client = self.app.test_client()

    def token(self, client=None):
        response = (client or self.client).get('/learn')
        # Curriculum has no forms; context processor still establishes the token.
        with (client or self.client).session_transaction() as session:
            return session['lab_token']

    def quiz(self, module=None, answers=None, client=None):
        module = module or MODULES[0]
        values = {f'q{i}':str(q['answer']) for i,q in enumerate(module['questions'])} if answers is None else answers
        return (client or self.client).post('/learn/'+module['id']+'/quiz',data={**values,'_lab_token':self.token(client)})

    def test_complete_curriculum_graph_and_pages(self):
        self.assertEqual(len(MODULES),12)
        self.assertEqual(sum(len(item['questions']) for item in MODULES),48)
        covered = set()
        seen = set()
        for item in MODULES:
            self.assertTrue(set(item['prerequisites']) <= seen)
            seen.add(item['id'])
            covered.update(item['lab_numbers'])
            response = self.client.get('/learn/'+item['id'])
            self.assertEqual(response.status_code,200)
            self.assertNotIn('quiz-feedback',response.text)
            for section in item['sections']:
                self.assertGreater(sum(len(p) for p in section['paragraphs']),250)
            self.assertEqual(self.quiz(item).status_code,200)
        self.assertEqual(covered,set(range(1,len(LABS)+1)))
        with connect(self.root/'dashboard.sqlite3') as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM lesson_results WHERE best_score=100').fetchone()[0],12)

    def test_grading_feedback_best_score_and_attempts(self):
        response = self.quiz()
        self.assertIn('Nilai 100 / 100',response.text)
        self.assertIn(MODULES[0]['questions'][0]['explanation'],response.text)
        wrong = {f'q{i}':str((q['answer']+1)%len(q['options'])) for i,q in enumerate(MODULES[0]['questions'])}
        self.assertIn('Nilai 0 / 100',self.quiz(answers=wrong).text)
        with connect(self.root/'dashboard.sqlite3') as db:
            row = db.execute('SELECT * FROM lesson_results').fetchone()
        self.assertEqual((row['best_score'],row['last_score'],row['attempts']),(100,0,2))

    def test_invalid_answers_and_csrf_do_not_record_attempt(self):
        for answers in ({},{'q0':'99','q1':'0','q2':'0','q3':'0'},{'q0':['0','1'],'q1':'0','q2':'0','q3':'0'}):
            self.assertEqual(self.quiz(answers=answers).status_code,400)
        self.assertEqual(self.client.post('/learn/'+MODULES[0]['id']+'/quiz',data={}).status_code,403)
        with connect(self.root/'dashboard.sqlite3') as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM lesson_results').fetchone()[0],0)

    def test_learners_are_isolated_and_survive_restart(self):
        self.quiz()
        other = self.app.test_client()
        self.assertIn('Belum diuji',other.get('/learn').text)
        self.assertNotIn('Nilai terbaik 100%',other.get('/learn').text)
        cookie = self.client.get_cookie('lab_dashboard')
        restarted = create_dashboard(data_dir=self.root).test_client()
        restarted.set_cookie('lab_dashboard',cookie.value)
        self.assertIn('Nilai terbaik 100%',restarted.get('/learn').text)

    def test_notes_escaped_bounded_and_exported_for_current_learner(self):
        module = MODULES[0]['id']
        text = '</textarea><script>alert(1)</script> BUKTI-PRIBADI'
        response = self.client.post(f'/learn/{module}/notes',data={'_lab_token':self.token(),'note':text},follow_redirects=True)
        self.assertIn('&lt;/textarea&gt;&lt;script&gt;',response.text)
        self.assertNotIn('<script>alert(1)</script>',response.text)
        response = self.client.get('/learning-report.md')
        self.assertIn('attachment',response.headers['Content-Disposition'])
        self.assertIn('BUKTI-PRIBADI',response.text)
        self.assertNotIn('BUKTI-PRIBADI',self.app.test_client().get('/learning-report.md').text)
        response = self.client.post(f'/learn/{module}/notes',data={'_lab_token':self.token(),'note':'x'*4001})
        self.assertEqual(response.status_code,400)
        self.assertEqual(self.client.get('/learn/not-a-module').status_code,404)


if __name__ == '__main__':
    unittest.main()
