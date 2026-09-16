export const API=process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export function getToken(){if(typeof window==="undefined") return ""; return localStorage.getItem("agrici_access_token")||"";}
export function setTokens(access:string,refresh?:string){localStorage.setItem("agrici_access_token",access);if(refresh)localStorage.setItem("agrici_refresh_token",refresh);}
export async function api(path:string,options:RequestInit={}){
 const token=getToken(); const headers=new Headers(options.headers);
 if(!headers.has("Content-Type")) headers.set("Content-Type","application/json");
 if(token) headers.set("Authorization",`Bearer ${token}`);
 const r=await fetch(`${API}${path}`,{...options,headers});
 const data=await r.json().catch(()=>({}));
 if(!r.ok) throw new Error(data?.error?.message||data?.detail||"AGRI-CI request failed");
 return data;
}
