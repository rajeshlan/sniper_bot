# test_sniper.py
import unittest
from unittest.mock import patch
from sniper import determine_blockchain, process_token

class TestSniperFunctions(unittest.TestCase):
    def test_determine_blockchain_eth(self):
        eth_tokens = ["ETH_TOKEN"]
        bsc_tokens = []
        sol_tokens = []
        self.assertEqual(determine_blockchain("ETH_TOKEN", eth_tokens, bsc_tokens, sol_tokens), "ETH")

    def test_determine_blockchain_bsc(self):
        eth_tokens = []
        bsc_tokens = ["BSC_TOKEN"]
        sol_tokens = []
        self.assertEqual(determine_blockchain("BSC_TOKEN", eth_tokens, bsc_tokens, sol_tokens), "BSC")

    def test_determine_blockchain_sol(self):
        eth_tokens = []
        bsc_tokens = []
        sol_tokens = ["SOL_TOKEN"]
        self.assertEqual(determine_blockchain("SOL_TOKEN", eth_tokens, bsc_tokens, sol_tokens), "SOL")

    def test_determine_blockchain_unknown(self):
        eth_tokens = []
        bsc_tokens = []
        sol_tokens = []
        with self.assertLogs(level='ERROR') as log:
            self.assertIsNone(determine_blockchain("UNKNOWN_TOKEN", eth_tokens, bsc_tokens, sol_tokens))
            self.assertIn("Unknown blockchain for token: UNKNOWN_TOKEN", log.output[0])

    @patch('sniper.analyze_token')
    @patch('sniper.buy_token')
    @patch('sniper.logging')
    def test_process_token_purchase(self, mock_logging, mock_buy_token, mock_analyze_token):
        mock_analyze_token.return_value = True
        process_token("ETH_TOKEN", ["ETH_TOKEN"], [], [])
        mock_buy_token.assert_called_once_with("ETH_TOKEN", float("MAX_INVESTMENT_AMOUNT"), "ETH")
        mock_logging.info.assert_called_with("Purchased ETH_TOKEN on ETH.")

    @patch('sniper.analyze_token')
    @patch('sniper.logging')
    def test_process_token_no_purchase(self, mock_logging, mock_analyze_token):
        mock_analyze_token.return_value = False
        process_token("ETH_TOKEN", ["ETH_TOKEN"], [], [])
        mock_logging.info.assert_called_with("Token ETH_TOKEN did not pass analysis.")

    @patch('sniper.analyze_token')
    @patch('sniper.buy_token')
    @patch('sniper.logging')
    def test_process_token_purchase_failure(self, mock_logging, mock_buy_token, mock_analyze_token):
        mock_analyze_token.return_value = True
        mock_buy_token.side_effect = Exception("Purchase failed")
        process_token("ETH_TOKEN", ["ETH_TOKEN"], [], [])
        mock_logging.error.assert_called_with("Failed to buy ETH_TOKEN on ETH: Purchase failed")

if __name__ == "__main__":
    unittest.main()
