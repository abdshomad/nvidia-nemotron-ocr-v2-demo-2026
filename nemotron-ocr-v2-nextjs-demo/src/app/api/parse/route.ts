import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const API_URL = process.env.API_URL || "http://localhost:8000/layout-parsing";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const {
      file, // base64 representation from client
      examplePath, // e.g., "/examples/complex/vl1_6_1.png"
      useLayoutDetection,
      promptLabel,
      useChartRecognition,
      useDocUnwarping,
      useDocOrientationClassify,
    } = body;

    let b64Image = "";

    // Resolve image data
    if (file) {
      b64Image = file;
    } else if (examplePath) {
      const cleanPath = examplePath.startsWith("/") ? examplePath.slice(1) : examplePath;
      
      const searchPaths = [
        path.join("/app", cleanPath),
        path.join(process.cwd(), cleanPath),
        path.join(process.cwd(), "public", cleanPath),
      ];

      let targetPath = "";
      for (const p of searchPaths) {
        if (fs.existsSync(p)) {
          targetPath = p;
          break;
        }
      }

      if (!targetPath) {
        console.error(`Example file not found in paths:`, searchPaths);
        return NextResponse.json(
          { error: `Example file not found: ${examplePath}` },
          { status: 404 }
        );
      }

      const fileBuffer = fs.readFileSync(targetPath);
      b64Image = fileBuffer.toString("base64");
    } else {
      return NextResponse.json(
        { error: "No image source provided (file or examplePath)" },
        { status: 400 }
      );
    }

    // Map PaddleOCR options to Nemotron options
    let merge_level = "layout";
    if (useLayoutDetection) {
      merge_level = "layout";
    } else if (promptLabel === "spotting") {
      merge_level = "paragraph";
    } else if (promptLabel === "formula") {
      merge_level = "word";
    } else {
      merge_level = "sentence";
    }

    // Determine model
    let model = "Multilingual (en, zh, ja, ko, ru, …)";
    if (promptLabel === "formula") {
      model = "English-only";
    }

    const payload = {
      file: b64Image,
      model: model,
      merge_level: merge_level
    };

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "Client-Platform": "nextjs-demo",
    };

    console.log(`Forwarding request to Nemotron API: ${API_URL}`);
    const response = await fetch(API_URL, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Nemotron API returned status ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Error in parse handler:", error);
    return NextResponse.json(
      { error: error.message || "Failed to process parsing request" },
      { status: 500 }
    );
  }
}
