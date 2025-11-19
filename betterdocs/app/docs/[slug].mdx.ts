// pages/docs/[slug].mdx.ts
import fs from 'fs';
import path from 'path';
import { NextApiRequest, NextApiResponse } from 'next';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const { slug } = req.query;
  const filePath = path.join(process.cwd(), 'content/docs', `${slug}.mdx`);

  try {
    const content = fs.readFileSync(filePath, 'utf8');
    res.setHeader('Content-Type', 'text/plain');
    res.status(200).send(content);
  } catch (_err) {
    res.status(404).send('File not found');
  }
}
