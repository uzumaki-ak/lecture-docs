import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Just let Next.js handle routing - client-side checks in pages will handle auth
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/auth/:path*"],
};

