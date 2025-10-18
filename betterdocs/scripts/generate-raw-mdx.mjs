import { readFile, writeFile, mkdir, readdir } from 'fs/promises';
import { join, dirname, relative, sep } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

async function getAllMdxFiles(dir, fileList = []) {
  const files = await readdir(dir, { withFileTypes: true });
  
  for (const file of files) {
    const filePath = join(dir, file.name);
    
    if (file.isDirectory()) {
      await getAllMdxFiles(filePath, fileList);
    } else if (file.name.endsWith('.mdx')) {
      fileList.push(filePath);
    }
  }
  
  return fileList;
}

async function generateRawMDX() {
  const outDir = join(__dirname, '..', 'out');
  const contentDir = join(__dirname, '..', 'content', 'docs');
  
  // Get all MDX files from content directory
  const mdxFiles = await getAllMdxFiles(contentDir);
  
  console.log(`Generating ${mdxFiles.length} raw MDX files...`);

  for (const mdxFilePath of mdxFiles) {
    try {
      // Read the MDX content
      const rawContent = await readFile(mdxFilePath, 'utf-8');
      
      // Get relative path from content/docs
      const relativePath = relative(contentDir, mdxFilePath);
      
      // Convert path to slug (remove .mdx extension and handle index files)
      let slugPath = relativePath.replace(/\\/g, '/').replace(/\.mdx$/, '');
      
      // If it's an index file, use the directory path
      if (slugPath.endsWith('/index')) {
        slugPath = slugPath.replace(/\/index$/, '');
      }
      
      // Build output path
      const outputPath = join(outDir, 'docs', `${slugPath}.mdx`);
      
      // Create directory if it doesn't exist
      const dir = dirname(outputPath);
      await mkdir(dir, { recursive: true });
      
      // Write the raw MDX file
      await writeFile(outputPath, rawContent, 'utf-8');
      
      console.log(`✓ Generated: /docs/${slugPath}.mdx`);
    } catch (error) {
      console.error(`✗ Failed to generate ${mdxFilePath}:`, error.message);
    }
  }

  console.log('✓ All raw MDX files generated successfully!');
}

generateRawMDX().catch(console.error);
