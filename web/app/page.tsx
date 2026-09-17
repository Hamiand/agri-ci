import Link from "next/link";
export default function Home(){
 return <main className="landing">
  <section className="hero">
   <div className="brandMark">A</div>
   <p className="eyebrow">AGRI-CI • CÔTE D’IVOIRE</p>
   <h1>De nos villages<br/>vers un avenir meilleur.</h1>
   <p className="lead">Produire. Regrouper. Vendre. Transporter. Être payé.</p>
   <div className="actions"><Link className="primary" href="/login">SE CONNECTER À AGRI-CI</Link></div>
   <p className="lead">Après connexion, AGRI-CI ouvre automatiquement l’espace autorisé : Producteur, Acheteur ou Opérations.</p>
  </section>
  <section className="promise"><b>Un marché avant la récolte.</b><span>AGRI-CI rapproche la production réelle de la demande réelle.</span></section>
 </main>
}