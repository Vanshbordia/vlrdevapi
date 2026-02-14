"use client"
import '@/app/global.css';
import { RootProvider } from 'fumadocs-ui/provider/next';
import SearchDialog from '@/components/search';
import Script from "next/script";
import { GoogleAnalytics } from '@next/third-parties/google'

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@6..144,1..1000&display=swap');
          body { font-family: 'Google Sans Flex', sans-serif; }
        `}</style>
        <meta name="google-site-verification" content="yVaBi-Tr3-OH7NnWQ8GPL1vbkqC_FOXAEQPlbSLKdsE" />
<script async src="https://www.googletagmanager.com/gtag/js?id=G-1JK0R2BGKW"></script>
      </head>
      <body className="flex flex-col min-h-screen">
         <GoogleAnalytics gaId="G-1JK0R2BGKW"/>
        <RootProvider
          search={{
            SearchDialog,
          }}>{children}</RootProvider>
      </body>
    </html>
  );
}
