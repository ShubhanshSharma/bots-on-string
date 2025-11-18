import * as pdfjsLib from "pdfjs-dist/legacy/build/pdf.mjs";

// Disable workers completely (legacy build supports this)
pdfjsLib.GlobalWorkerOptions.workerSrc = "";

export async function extractTextFromPDF(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();

  const pdf = await pdfjsLib.getDocument({
    data: buffer,
  }).promise;

  let text = "";

  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    const pageText = content.items
      .map((item: unknown) => (item as { str: string }).str)
      .join(" ");
    text += pageText + "\n";
  }

  return text.trim();
}
