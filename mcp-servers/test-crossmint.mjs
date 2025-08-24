import axios from 'axios';
import dotenv from 'dotenv';
dotenv.config();

console.log('Testing Crossmint Connection...');
console.log('API Key:', process.env.CROSSMINT_API_KEY ? 'Set' : 'Not Set');

async function testCrossmint() {
  try {
    // Farmer Ted's wallet address
    const walletAddress = process.env.FARMER_TED_WALLET_ADDRESS;
    
    console.log('\n--- Getting Wallet Balance ---');
    console.log('Wallet Address:', walletAddress);
    
    // Try to get wallet balance
    const response = await axios.get(
      `https://staging.crossmint.com/api/2025-06-09/wallets/${walletAddress}/balances`,
      {
        headers: {
          'x-api-key': process.env.CROSSMINT_API_KEY || ''
        }
      }
    );
    
    console.log('Response:', JSON.stringify(response.data, null, 2));
    
    // Look for USDC balance
    const tokens = response.data.tokens || [];
    const usdcToken = tokens.find(token => token.symbol === 'USDC');
    
    if (usdcToken) {
      console.log('\n--- USDC Balance Found ---');
      console.log('Amount:', usdcToken.balance);
      console.log('Decimals:', usdcToken.decimals);
      console.log('Actual Value:', parseFloat(usdcToken.balance) / Math.pow(10, usdcToken.decimals));
    } else {
      console.log('\nNo USDC balance found in wallet');
    }
    
  } catch (error) {
    console.error('\nError:', error.message);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    }
    
    // Try alternative endpoint
    console.log('\n--- Trying alternative endpoint ---');
    try {
      const response2 = await axios.get(
        'https://staging.crossmint.com/api/2025-06-09/wallets/userId:farmer-ted:evm/tokens/ethereum-sepolia:usdc',
        {
          headers: {
            'x-api-key': process.env.CROSSMINT_API_KEY || ''
          }
        }
      );
      console.log('Alternative response:', JSON.stringify(response2.data, null, 2));
    } catch (error2) {
      console.error('Alternative also failed:', error2.message);
    }
  }
}

testCrossmint();