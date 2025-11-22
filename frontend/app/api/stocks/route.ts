import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const symbols = searchParams.get('symbols') || 'SPY,QQQ,NVDA,TSLA';

  try {
    // Fetch from the Python backend
    const backendUrl = `http://localhost:8000/api/stock/quotes?symbols=${symbols}`;
    const response = await fetch(backendUrl, {
      headers: {
        'Accept': 'application/json',
      },
      next: { revalidate: 30 } // Cache for 30 seconds to be polite to limits
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Stock API Proxy Error:", error);
    return NextResponse.json(
      { error: "Failed to fetch stock data" },
      { status: 500 }
    );
  }
}

