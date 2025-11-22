import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Expanded list of "hyped" and major coins
    const coins = [
      'bitcoin',
      'ethereum',
      'solana',
      'dogecoin',
      'xrp',
      'cardano',
      'shiba-inu',
      'pepe',
      'sui',
      'bonk'
    ].join(',');

    const response = await fetch(`https://api.coincap.io/v2/assets?ids=${coins}`, {
      headers: {
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
      },
      next: { revalidate: 10 } // Cache for 10 seconds
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`CoinCap API error (${response.status}):`, errorText);
      throw new Error(`CoinCap API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Market API Error:", error);
    // Return more specific error details if available, but safe for client
    return NextResponse.json(
      { error: "Failed to fetch market data", details: error.message },
      { status: 500 }
    );
  }
}
