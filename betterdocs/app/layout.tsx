"use client"
import '@/app/global.css';
import { RootProvider } from 'fumadocs-ui/provider/next';
import SearchDialog from '@/components/search';

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@6..144,1..1000&display=swap');
          body { font-family: 'Google Sans Flex', sans-serif; }
        `}</style>
      </head>
      <body className="flex flex-col min-h-screen">
        <RootProvider
          search={{
            SearchDialog,
          }}>{children}</RootProvider>
      </body>
    </html>
  );
}
