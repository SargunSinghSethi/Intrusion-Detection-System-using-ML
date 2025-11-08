import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs";

const BACKEND_URL = process.env.FASTAPI_BACKEND_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  const { userId, getToken } = auth();
  if (!userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const token = await getToken();
  const body = await req.json();

  const response = await fetch(`${BACKEND_URL}/merge-chunks`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
