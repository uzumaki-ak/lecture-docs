import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { proxy: string[] } }
) {
  const proxyPath = params.proxy.join('/');
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
  
  try {
    const response = await fetch(`${backendUrl}/api/${proxyPath}${request.nextUrl.search}`, {
      headers: request.headers,
    });
    
    const data = await response.json();
    
    return NextResponse.json(data, {
      status: response.status,
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to proxy request' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { proxy: string[] } }
) {
  const proxyPath = params.proxy.join('/');
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
  
  try {
    const body = await request.json();
    
    const response = await fetch(`${backendUrl}/api/${proxyPath}`, {
      method: 'POST',
      headers: request.headers,
      body: JSON.stringify(body),
    });
    
    const data = await response.json();
    
    return NextResponse.json(data, {
      status: response.status,
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to proxy request' },
      { status: 500 }
    );
  }
}