import * as fs from 'fs';
import * as path from 'path';
import { formatOutput } from './formatter';

function inferFormat(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === '.json') return 'json';
  if (ext === '.csv') return 'csv';
  if (ext === '.html' || ext === '.htm') return 'html';
  if (ext === '.txt') return 'text';
  return 'json';
}

export async function writeOutput(
  result: unknown,
  outputPath: string,
  format?: string
): Promise<void> {
  const chosenFormat = (format && format.trim().length > 0)
    ? format.toLowerCase()
    : inferFormat(outputPath);

  const content = formatOutput(result, chosenFormat);
  fs.writeFileSync(outputPath, content, 'utf-8');
}
