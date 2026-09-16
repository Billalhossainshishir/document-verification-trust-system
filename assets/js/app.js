const KEY="trustdoc-demo-v1";
const SAMPLE="DOCUMENT VERIFICATION DEMO\nDocument: Certificate of Completion\nRecipient: Portfolio Recruiter Demo\nIssuer: TrustDoc Sample Authority\nIssue Date: 16 September 2026\nReference: TD-2026-001\n";
const MODIFIED=SAMPLE.replace("TD-2026-001","TD-2026-001-MODIFIED");
let state=load(); let latest=state.receipts[0]||null;
function load(){try{return JSON.parse(localStorage.getItem(KEY))||{documents:[],events:[],attempts:[],receipts:[]}}catch{return{documents:[],events:[],attempts:[],receipts:[]}}}
function save(){localStorage.setItem(KEY,JSON.stringify(state));render()}
function makeId(p){return p+"-"+crypto.randomUUID().replaceAll("-","").slice(0,10).toUpperCase()}
async function hash(file){const b=await file.arrayBuffer();const h=await crypto.subtle.digest("SHA-256",b);return [...new Uint8Array(h)].map(x=>x.toString(16).padStart(2,"0")).join("")}
function dl(name,text){const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([text],{type:"text/plain"}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500)}
function event(type,message,status=""){state.events.unshift({type,message,status,at:new Date().toISOString()});state.events=state.events.slice(0,30)}
function esc(s){return String(s).replace(/[&<>'"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]))}
async function register(){
  const f=document.querySelector("#registerFile").files[0]; if(!f)return alert("Choose a document first.");
  const d={document_id:makeId("DOC"),verification_id:makeId("VER"),filename:f.name,size:f.size,sha256:await hash(f),registered_at:new Date().toISOString(),document_type:document.querySelector("#docType").value||"Unspecified",registered_by:document.querySelector("#registeredBy").value||"Portfolio Demo"};
  state.documents.unshift(d); document.querySelector("#verificationId").value=d.verification_id; event("DOCUMENT_REGISTERED",d.filename+" fingerprint registered.","ok"); save();
  const out=document.querySelector("#registerOut"); out.className="result"; out.innerHTML="<b>Fingerprint registered</b><p>"+d.verification_id+"</p><p class='mono'>SHA-256 "+d.sha256+"</p><small>Browser demo stores fingerprint metadata only, not the file bytes.</small>";
  const badge=document.querySelector("#registerBadge");badge.textContent="Registered";badge.className="badge ok";
}
async function verify(){
  const id=document.querySelector("#verificationId").value.trim(),f=document.querySelector("#verifyFile").files[0]; if(!id||!f)return alert("Enter a Verification ID and choose a candidate file.");
  const d=state.documents.find(x=>x.verification_id===id); if(!d)return alert("Verification ID is not in this browser demo.");
  const candidate=await hash(f),status=candidate===d.sha256?"VERIFIED":"FAILED";
  const a={attempt_id:makeId("ATT"),verification_id:id,document_id:d.document_id,candidate_filename:f.name,candidate_sha256:candidate,status,verified_at:new Date().toISOString()}; state.attempts.unshift(a);
  const r={receipt_id:makeId("RCP"),verification_id:id,document_id:d.document_id,document:d.filename,candidate_document:f.name,status,registered_at:d.registered_at,verified_at:a.verified_at,registered_sha256:d.sha256,candidate_sha256:candidate,note:"Static demo receipt. Full backend signs canonical JSON receipts with Ed25519."}; state.receipts.unshift(r);latest=r;
  event(status==="VERIFIED"?"VERIFICATION_SUCCESS":"VERIFICATION_FAILED",f.name+": "+status,status==="VERIFIED"?"ok":"bad");event("RECEIPT_GENERATED",r.receipt_id+" generated.",status==="VERIFIED"?"ok":"bad");save();
  const badge=document.querySelector("#verifyBadge");badge.textContent=status;badge.className="badge "+(status==="VERIFIED"?"ok":"bad");
  const out=document.querySelector("#verifyOut");out.className="result";out.innerHTML="<b>"+(status==="VERIFIED"?"✓ Integrity verified":"✕ Verification failed")+"</b><p>"+(status==="VERIFIED"?"Fingerprints match exactly.":"Candidate fingerprint differs.")+"</p><p class='mono'>Registered: "+d.sha256+"<br>Candidate: "+candidate+"</p>";
}
function render(){
  document.querySelector("#registeredMetric").textContent=state.documents.length;
  document.querySelector("#successMetric").textContent=state.attempts.filter(x=>x.status==="VERIFIED").length;
  document.querySelector("#failedMetric").textContent=state.attempts.filter(x=>x.status==="FAILED").length;
  document.querySelector("#receiptMetric").textContent=state.receipts.length;
  document.querySelector("#auditList").innerHTML=state.events.length?state.events.map(e=>"<div class='audit "+e.status+"'><b>"+esc(e.type)+"</b><br><small>"+esc(e.message)+" · "+new Date(e.at).toLocaleString()+"</small></div>").join(""):"<p class='muted'>No activity yet.</p>";
  const r=latest||state.receipts[0]; const body=document.querySelector("#receiptBody");
  if(!r){body.innerHTML="<p class='muted'>A receipt appears after verification.</p>";return}
  body.innerHTML="<div class='receiptline'><span>Receipt ID</span><b>"+r.receipt_id+"</b></div><div class='receiptline'><span>Status</span><b>"+r.status+"</b></div><div class='receiptline'><span>Verification ID</span><b>"+r.verification_id+"</b></div><div class='receiptline'><span>Document</span><b>"+esc(r.document)+"</b></div><div class='receiptline'><span>SHA-256</span><span class='mono'>"+r.candidate_sha256+"</span></div><div class='actions'><button class='btn' id='downloadReceipt'>Download JSON receipt</button><a class='btn' href='verify.html?id="+encodeURIComponent(r.verification_id)+"'>Public record</a></div><p class='muted small'>"+esc(r.note)+"</p>";
  document.querySelector("#downloadReceipt").onclick=()=>dl(r.receipt_id+".json",JSON.stringify(r,null,2));
}
document.querySelector("#downloadSample").onclick=()=>dl("trustdoc_sample_certificate.txt",SAMPLE);
document.querySelector("#downloadModified").onclick=()=>dl("trustdoc_modified_certificate.txt",MODIFIED);
document.querySelector("#registerBtn").onclick=register;document.querySelector("#verifyBtn").onclick=verify;
document.querySelector("#resetBtn").onclick=()=>{if(confirm("Clear browser demo records?")){localStorage.removeItem(KEY);state={documents:[],events:[],attempts:[],receipts:[]};latest=null;render()}};
render();
