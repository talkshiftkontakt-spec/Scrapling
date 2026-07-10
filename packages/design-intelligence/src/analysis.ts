import OpenAI from "openai";
import { GoogleGenAI } from "@google/genai";

import {
  analysisResultSchema,
  AppError,
  readEnv,
  type AnalysisResult,
  type ScreenshotArtifact
} from "@design-intelligence/shared";

const env = readEnv();

export interface AnalysisInput {
  websiteId: string;
  screenshot: ScreenshotArtifact;
  promptVersion?: string;
}

export class VisualAnalysisService {
  private readonly openAi = env.OPENAI_API_KEY ? new OpenAI({ apiKey: env.OPENAI_API_KEY }) : null;
  private readonly gemini = env.GEMINI_API_KEY ? new GoogleGenAI({ apiKey: env.GEMINI_API_KEY }) : null;

  public async analyze(provider: "openai" | "gemini", input: AnalysisInput): Promise<AnalysisResult> {
    const rawResponse = provider === "openai"
      ? await this.analyzeWithOpenAI(input)
      : await this.analyzeWithGemini(input);

    return analysisResultSchema.parse({
      websiteId: input.websiteId,
      modelProvider: provider,
      model: provider === "openai" ? "gpt-4.1-mini" : "gemini-2.5-flash",
      ...rawResponse,
      rawResponse: JSON.stringify(rawResponse)
    });
  }

  private async analyzeWithOpenAI(input: AnalysisInput): Promise<Omit<AnalysisResult, "websiteId" | "modelProvider" | "model" | "rawResponse">> {
    if (!this.openAi) {
      throw new AppError("missing_openai_key", "OPENAI_API_KEY is required for OpenAI analysis.", 500);
    }

    const response = await this.openAi.responses.create({
      model: "gpt-4.1-mini",
      input: [
        {
          role: "system",
          content: [{ type: "input_text", text: "Analyze premium web design screenshots and return structured JSON only." }]
        },
        {
          role: "user",
          content: [
            { type: "input_text", text: `Analyze screenshot for website ${input.websiteId}: ${input.screenshot.screenshotDriveUrl}` }
          ]
        }
      ],
      text: {
        format: {
          type: "json_schema",
          name: "design_analysis",
          strict: true,
          schema: {
            type: "object",
            additionalProperties: false,
            properties: {
              style: { type: "string" },
              industry: { type: "string" },
              typography: { type: "array", items: { type: "string" } },
              colourPalette: { type: "array", items: { type: "string" } },
              layout: { type: "string" },
              visualDensity: { type: "string" },
              navigationStyle: { type: "string" },
              designKeywords: { type: "array", items: { type: "string" } },
              summary: { type: "string" },
              mobileFirstLikelihood: { type: "number" },
              animationLikelihood: { type: "number" },
              designMaturity: { type: "string" }
            },
            required: ["style", "industry", "typography", "colourPalette", "layout", "visualDensity", "navigationStyle", "designKeywords", "summary", "mobileFirstLikelihood", "animationLikelihood", "designMaturity"]
          }
        }
      }
    });

    return JSON.parse(response.output_text) as Omit<AnalysisResult, "websiteId" | "modelProvider" | "model" | "rawResponse">;
  }

  private async analyzeWithGemini(input: AnalysisInput): Promise<Omit<AnalysisResult, "websiteId" | "modelProvider" | "model" | "rawResponse">> {
    if (!this.gemini) {
      throw new AppError("missing_gemini_key", "GEMINI_API_KEY is required for Gemini analysis.", 500);
    }

    const response = await this.gemini.models.generateContent({
      model: "gemini-2.5-flash",
      contents: `Analyze screenshot for website ${input.websiteId}: ${input.screenshot.screenshotDriveUrl}. Return JSON with style, industry, typography, colourPalette, layout, visualDensity, navigationStyle, designKeywords, summary, mobileFirstLikelihood, animationLikelihood, designMaturity.`
    });

    const text = response.text ?? "{}";
    return JSON.parse(text) as Omit<AnalysisResult, "websiteId" | "modelProvider" | "model" | "rawResponse">;
  }
}
