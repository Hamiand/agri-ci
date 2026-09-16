import Link from "next/link";
export default function WorkflowHeader({title,subtitle}:{title:string,subtitle:string}){
 return <header className="workflowHeader"><Link href="/farmer">‹ Retour</Link><span>AGRI-CI PRODUCTEUR</span><h1>{title}</h1><p>{subtitle}</p></header>
}