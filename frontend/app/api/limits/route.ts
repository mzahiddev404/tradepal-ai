import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Fetch from the Python backend
    const backendUrl = `http://localhost:8000/api/stock/limits`;
    const response = await fetch(backendUrl, {
      headers: {
        'Accept': 'application/json',
      },
      next: { revalidate: 60 } // Cache for 60 seconds
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Limits API Proxy Error:", error);
    return NextResponse.json(
      { error: "Failed to fetch limits" },
      { status: 500 }
    );
  }
}

