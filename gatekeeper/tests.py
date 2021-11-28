from testing.TwitterTestCase import TwitterTestCase
from gatekeeper.models import GateKeeper


class GateKeeperTests(TwitterTestCase):

    def setUp(self):
        self.clear_cache()

    def test_gatekeeper(self):
        gk = GateKeeper.get('gk_name')
        self.assertEqual(gk, {'percent': 0, 'description': ''})
        self.assertEqual(GateKeeper.is_switch_on('gk_name'), False)
        self.assertEqual(GateKeeper.in_gk('gk_name', 1), False)

        GateKeeper.set_kv('gk_name', 'percent', 20)
        self.assertEqual(GateKeeper.is_switch_on('gk_name'), False)
        self.assertEqual(GateKeeper.in_gk('gk_name', 1), True)

        GateKeeper.set_kv('gk_name', 'percent', 100)
        self.assertEqual(GateKeeper.is_switch_on('gk_name'), True)
        self.assertEqual(GateKeeper.in_gk('gk_name', 1), True)