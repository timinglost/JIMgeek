import unittest, time
from utils import load_config
from client import create_massege, response_treatment


class CreateMassegeAndResponseTreatmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self._config = load_config()
        self._dict_all = {
                "action": self._config['PRESENCE'],
                "time": time.time(),
                "type": "status",
                "user": {
                        "account_name":  'Ivan',
                        "status":      "Yep, I am here!"
                }
        }
        self._dict_count = len(self._dict_all)
        self._server_answer = {"response": '200',
                               "time": time.time(),
                               "alert": "успешное завершение"}
        self._run_answer = f'"response": {self._server_answer["response"]}\n"time": {self._server_answer["time"]}\n"alert": {self._server_answer["alert"]}'
        self._count_run_answer = len(self._run_answer)

    def test_create_massege_filling_dict(self):
        self.assertEqual(create_massege(self._config), self._dict_all)

    def test_create_massege_count_dict(self):
        self.assertEqual(len(create_massege(self._config)), self._dict_count)

    def test_response_treatment_filling_dict(self):
        self.assertEqual(response_treatment(self._server_answer, self._config), self._run_answer)

    def test_response_treatment_count_dict(self):
        self.assertEqual(len(response_treatment(self._server_answer, self._config)), self._count_run_answer)


if __name__ == '__main__':
    unittest.main()
