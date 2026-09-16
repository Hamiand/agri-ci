import FarmerAction from "@/components/FarmerAction";
export default function FarmerHome(){
 return <main className="phoneShell">
  <header className="farmerHeader"><div><span className="mini">AGRI-CI PRODUCTEUR</span><h1>Bonjour Koffi</h1>
  <p>Que voulez-vous faire aujourd’hui ?</p></div><div className="avatar">K</div></header>
  <section className="statusCard"><div><span>Prochaine récolte</span><b>Tomates • 500 kg</b><small>Prévue : 16–18 mai 2027</small></div><span className="pill">ANNONCÉE</span></section>
  <section className="menu">
   <FarmerAction icon="◉" title="VENDRE" subtitle="Mettre une quantité sur AGRI-CI" href="/farmer/sell"/>
   <FarmerAction icon="⌁" title="ANNONCER MA PROCHAINE RÉCOLTE" subtitle="Préparer le marché avant la récolte" href="/farmer/harvest"/>
   <FarmerAction icon="◎" title="VOIR CE QUE LES ACHETEURS RECHERCHENT" subtitle="Demandes actives près de vous" href="/farmer/demands"/>
   <FarmerAction icon="✓" title="PROPOSITIONS AGRI-CI" subtitle="Accepter ou refuser une demande" href="/farmer/commitments"/>
   <FarmerAction icon="↗" title="VOIR LES PRIX" subtitle="Suivre les tendances du marché"/>
   <FarmerAction icon="▶" title="VENDRE EN DIRECT" subtitle="Présenter votre plantation"/>
   <FarmerAction icon="⚖" title="COLLECTE" subtitle="Poids réel et remise des produits" href="/farmer/collection"/>
   <FarmerAction icon="▣" title="DEMANDER UN TRANSPORT" subtitle="Organiser collecte et livraison"/>
   <FarmerAction icon="₣" title="MON ARGENT" subtitle="Paiements et historique" href="/farmer/money"/>
   <FarmerAction icon="♪" title="ÉCOUTER" subtitle="Utiliser AGRI-CI avec la voix"/>
  </section>
  <nav className="bottomNav"><span>⌂<small>Accueil</small></span><span>▤<small>Marché</small></span><span>◎<small>Activité</small></span><span>●<small>Profil</small></span></nav>
 </main>
}