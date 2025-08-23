import Alpaca from '@alpacahq/alpaca-trade-api';
import dotenv from 'dotenv';
dotenv.config();

console.log('Testing Alpaca Connection...');
console.log('API Key:', process.env.ALPACA_API_KEY ? 'Set' : 'Not Set');
console.log('Secret Key:', process.env.ALPACA_SECRET_KEY ? 'Set' : 'Not Set');

const alpaca = new Alpaca({
  keyId: process.env.ALPACA_API_KEY,
  secretKey: process.env.ALPACA_SECRET_KEY,
  paper: true,
  usePolygon: false
});

async function testAlpaca() {
  try {
    console.log('\n--- Getting Account Info ---');
    const account = await alpaca.getAccount();
    console.log('Account Status:', account.status);
    console.log('Cash:', account.cash);
    console.log('Portfolio Value:', account.portfolio_value);
    console.log('Buying Power:', account.buying_power);
    console.log('Equity:', account.equity);
    console.log('Last Equity:', account.last_equity);
    
    console.log('\n--- Getting Positions ---');
    const positions = await alpaca.getPositions();
    console.log('Number of positions:', positions.length);
    positions.forEach(pos => {
      console.log(`- ${pos.symbol}: ${pos.qty} shares @ $${pos.avg_entry_price}`);
    });
    
    console.log('\n--- Getting Recent Orders ---');
    const orders = await alpaca.getOrders({ limit: 5 });
    console.log('Recent orders:', orders.length);
    orders.forEach(order => {
      console.log(`- ${order.symbol}: ${order.side} ${order.qty} @ ${order.order_type}`);
    });
    
  } catch (error) {
    console.error('Error:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
}

testAlpaca();