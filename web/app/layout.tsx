import "./globals.css";
export const metadata={title:"AGRI-CI",description:"From our villages to a brighter tomorrow"};
export default function RootLayout({children}:{children:React.ReactNode}){
 return <html lang="fr"><body>{children}</body></html>
}