import FarmerAction from "@/components/FarmerAction";
export default function FarmerHome(){
 return <main className="phoneShell">
  <header className="farmerHeader"><div><span className="mini">AGRI-CI PRODUCTEUR</span><h1>Espace producteur</h1>
  <p>Que voulez-vous faire aujourd’hui ?</p></div><div className="avatar">P</div></header>
  <section className="statusCard"><div><span>Préparer votre marché</span><b>Annoncez votre récolte avant de vendre</b><small>AGRI-CI relie votre offre aux demandes des acheteurs.</small></div></section>
  <section className="menu">
   <FarmerAction icon="◉" title="VENDRE" subtitle="Mettre une quantité sur AGRI-CI" href="/farmer/sell"/>
   <FarmerAction icon="⌁" title="ANNONCER MA PROCHAINE RÉCOLTE" subtitle="Préparer le marché avant la récolte" href="/farmer/harvest"/>
   <FarmerAction icon="◎" title="VOIR CE QUE LES ACHETEURS RECHERCHENT" subtitle="Demandes actives" href="/farmer/demands"/>
   <FarmerAction icon="✓" title="PROPOSITIONS AGRI-CI" subtitle="Accepter ou refuser une demande" href="/farmer/commitments"/>
   <FarmerAction icon="⚖" title="MES COLLECTES" subtitle="Suivre les poids enregistrés par AGRI-CI" href="/farmer/collection"/>
   <FarmerAction icon="₣" title="MON ARGENT" subtitle="Paiements et historique" href="/farmer/money"/>
  </section>
  <nav className="bottomNav"><span>⌂<small>Accueil</small></span><span>▤<small>Marché</small></span><span>◎<small>Activité</small></span><span>●<small>Profil</small></span></nav>
 </main>
}