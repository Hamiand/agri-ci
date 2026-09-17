export const API=(process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/,"");

const ACCESS="agrici_access_token";
const REFRESH="agrici_refresh_token";

export function getToken(){if(typeof window==="undefined") return ""; return sessionStorage.getItem(ACCESS)||"";}
export function getRefreshToken(){if(typeof window==="undefined") return ""; return sessionStorage.getItem(REFRESH)||"";}
export function setTokens(access:string,refresh?:string){
 if(typeof window==="undefined") return;
 sessionStorage.setItem(ACCESS,access);
 if(refresh) sessionStorage.setItem(REFRESH,refresh);
}
export function clearTokens(){
 if(typeof window==="undefined") return;
 sessionStorage.removeItem(ACCESS);sessionStorage.removeItem(REFRESH);
}

async function parse(r:Response){return r.json().catch(()=>({}));}

async function refreshAccessToken(){
 const refresh=getRefreshToken();
 if(!refresh) return false;
 const r=await fetch(`${API}/auth/refresh`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({refresh_token:refresh})});
 if(!r.ok){clearTokens();return false;}
 const data=await parse(r);
 if(!data.access_token){clearTokens();return false;}
 setTokens(data.access_token,data.refresh_token||refresh);
 return true;
}

function mutationKey(method:string,headers:Headers){
 if(method==="GET" || method==="HEAD" || headers.has("Idempotency-Key")) return;
 const cryptoApi=globalThis.crypto;
 const key=cryptoApi?.randomUUID ? cryptoApi.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
 headers.set("Idempotency-Key",`web-${key}`);
}

export async function api(path:string,options:RequestInit={},retry=true){
 const token=getToken();const headers=new Headers(options.headers);
 const method=(options.method||"GET").toUpperCase();
 if(!headers.has("Content-Type") && options.body) headers.set("Content-Type","application/json");
 if(token) headers.set("Authorization",`Bearer ${token}`);
 mutationKey(method,headers);
 let r=await fetch(`${API}${path}`,{...options,method,headers});
 if(r.status===401 && retry && getRefreshToken()){
  const refreshed=await refreshAccessToken();
  if(refreshed) return api(path,{...options,method,headers},false);
 }
 const data=await parse(r);
 if(!r.ok) throw new Error(data?.error?.message||data?.detail||"AGRI-CI request failed");
 return data;
}
