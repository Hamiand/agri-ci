import Link from "next/link";
export default function FarmerAction({icon,title,subtitle,href="#"}:{icon:string,title:string,subtitle:string,href?:string}){
 return <Link href={href} className="farmerAction"><span className="icon">{icon}</span>
 <span><b>{title}</b><small>{subtitle}</small></span><strong>›</strong></Link>
}