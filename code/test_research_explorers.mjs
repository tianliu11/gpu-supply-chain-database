// Dependency-free JavaScript/DOM smoke tests; not a substitute for browser layout QA.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.handlers={};this.value='';this.textContent=''}
  setAttribute(k,v){this.attributes[k]=String(v)}
  append(...children){this.children.push(...children)}
  replaceChildren(...children){this.children=[...children]}
  addEventListener(k,v){this.handlers[k]=v}
  createTHead(){const e=new Element('thead');this.append(e);return e}
  createTBody(){const e=new Element('tbody');this.append(e);return e}
  insertRow(){const e=new Element('tr');this.append(e);return e}
  insertCell(){const e=new Element('td');this.append(e);return e}
}
function load(name){
  const file=fs.readFileSync(path.join(root,'figures',name),'utf8');
  const elements=new Map([...file.matchAll(/<[^>]+\bid="([^"]+)"/g)].map(m=>[m[1],new Element('div')]));
  const raw=file.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1];
  elements.get('data').textContent=raw;
  const context=vm.createContext({document:{
    getElementById:id=>{assert(elements.has(id),`Missing DOM target ${id}`);return elements.get(id)},
    createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag),
    createTextNode:t=>({textContent:t}),
  }});
  const script=file.match(/<script>([\s\S]*?)<\/script>/)[1];
  new vm.Script(script,{filename:name}).runInContext(context);
  assert(!/\b(fetch|XMLHttpRequest|WebSocket)\s*\(/.test(script),'Explorer must work without network calls');
  return {elements,context,data:JSON.parse(raw)};
}
const graph=load('full_supply_chain_structure.html');
assert.equal(graph.data.nodes.length,289);
assert.equal(graph.data.edges.length,757);
assert.match(graph.elements.get('selected').textContent,/Graphics Card/);
graph.elements.get('component').value='LD:synthesis_gas';
graph.elements.get('component').handlers.change();
assert.match(graph.elements.get('selected').textContent,/Synthesis gas/);
assert(graph.elements.get('vendors').children[0].children[1].children.length>0);
graph.elements.get('mode').value='overview';
graph.elements.get('mode').handlers.change();
assert.equal(graph.elements.get('graph').children.filter(e=>e.tag==='g').length,289);
const map=load('full_supply_chain_transport_map.html');
assert.equal(map.data.world.features.length,177);
assert(map.elements.get('map').children[0].children.length>100,'World geometry must exist');
map.elements.get('factory').value=map.data.facilities[0].facility_id;
map.elements.get('factory').handlers.change();
assert.equal(map.elements.get('hubtable').children[0].children[1].children.length,6);
map.elements.get('factory').value='';
map.elements.get('factory').handlers.change();
assert.equal(map.elements.get('hubtable').children.length,0,'All-site view must not retain stale selected-site rows');
console.log('Explorer JavaScript, embedded data, selection changes, full overview, basemap and hub-table smoke tests passed.');
