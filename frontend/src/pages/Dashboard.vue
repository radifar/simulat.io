<template>
  <div class="row">
    <div class="col-12">
      <base-input class= "col-md-4" v-model="workflow.name">
      </base-input>
      <div id="rete" class="node-editor">
        <base-button
            class="col-md-1"
            type="success"
            size="sm"
          >Load</base-button>
          <base-button
            class="col-md-1"
            type="success"
            size="sm"
          >Save</base-button>
          <base-button
            class="col-md-1"
            type="success"
            size="sm"
          >Run</base-button>
      </div>
    </div>
  </div>
</template>
<script>
import config from "@/config";
import Rete from "rete";
import * as VueRenderPlugin from "rete-vue-render-plugin";
import * as ConnectionPlugin from "rete-connection-plugin";
import * as CommentPlugin from "rete-comment-plugin";
import AreaPlugin from "rete-area-plugin";
import * as ContextMenuPlugin from "rete-context-menu-plugin";
import HistoryPlugin from "rete-history-plugin";
import * as ConnectionMasteryPlugin from "rete-connection-mastery-plugin";
import { saveAs } from "file-saver";

// Socket definition

var numSocket = new Rete.Socket("Number value");
var molSocket = new Rete.Socket("Molecule value");
var bindDefSocket = new Rete.Socket("Binding site definition");
var resultSocket = new Rete.Socket("Save result to DB")

/* 
  Vue Control
  1. VueNumControl
  2. VueTextControl
  3. VueOptControl
  4. VueCheckboxControl
  5. VueInputFileControl
*/

var VueNumControl = {
  props: ["readonly", "emitter", "ikey", "getData", "putData"],
  template:
    '<input type="number" :readonly="readonly" :value="value" @input="change($event)" @dblclick.stop="" @pointermove.stop=""/>',
  data() {
    return {
      value: 0
    };
  },
  methods: {
    change(e) {
      console.log(e)
      console.log(this.ikey)
      this.value = +e.target.value;
      this.update();
    },
    update() {
      if (this.ikey) this.putData(this.ikey, this.value);
      this.emitter.trigger("process");
    }
  },
  mounted() {
    this.value = this.getData(this.ikey);
  }
};

var VueTextControl = {
  props: ["readonly", "emitter", "ikey", "placeholder", "label", "getData", "putData"],
  template:
    '<div>\
    {{label}}\
    <input type="text" :placeholder="placeholder" :readonly="readonly" :value="value" @input="change($event)" @dblclick.stop="" @pointermove.stop=""/>\
    </div>',
  data() {
    return {
      value: 0
    };
  },
  methods: {
    change(e) {
      this.value = e.target.value;
      this.update();
    },
    update() {
      if (this.ikey) this.putData(this.ikey, this.value);
      this.emitter.trigger("process");
    }
  },
  mounted() {
    this.value = this.getData(this.ikey);
  }
};

var VueOptControl = {
  props: ["readonly", "emitter", "ikey", "options", "getData", "putData"],
  template:
    '<select :selected="selected" @input="change($event)" @mousewheel.stop="" @pointermove.stop="" @pointerdown.stop="">\
        <option v-for="option in options" :value="option.value">{{option.name}}</option>\
    </select>',
  data() {
    return {
      selected: null
    };
  },
  methods: {
    change(e) {
      this.selected = e.target.value;
      this.update();
    },
    update() {
      if (this.ikey) this.putData(this.ikey, this.selected);
      this.emitter.trigger("process");
      console.log(this.ikey);
      console.log(this.selected);
    }
  },
  mounted() {
    this.selected = this.getData(this.ikey);
  }
};

var VueCheckboxControl = {
  props: ["readonly", "emitter", "ikey", "label", "getData", "putData"],
  template:
  '<div>\
  <table><tr>\
  <td><div class="control-title">{{label}}:</div></td>\
  <td><input type="checkbox" :name="label"></td>\
  </tr></table>\
  </div>'
};

var VueInputFileControl = {
  props: ["readonly", "emitter", "ikey", "label", "getData", "putData"],
  template:
  '<div>\
  <div class="control-title">{{label}}:</div>\
  <input type="file" name="ligand" accept="text/*">\
  </div>'
};

/*
  Controller class:
  1. NumControl
  2. TextControl
  3. OptControl
  4. CheckboxControl
  5. InputFileControl
*/

class NumControl extends Rete.Control {
  constructor(emitter, key, readonly) {
    super(key);
    this.component = VueNumControl;
    this.props = { emitter, ikey: key, readonly };
  }
  setValue(val) {
    this.vueContext.value = val;
  }
}

class TextControl extends Rete.Control {
  constructor(emitter, key, placeholder, label, readonly) {
    super(key);
    this.component = VueTextControl;
    this.props = { emitter, ikey: key, placeholder, label, readonly };
  }
  setValue(val) {
    this.vueContext.value = val;
  }
}

class OptControl extends Rete.Control {
  constructor(emitter, key, options, readonly) {
    super(key);
    this.component = VueOptControl;
    this.props = { emitter, ikey: key, options, readonly };
  }
  setValue(val) {
    this.vueContext.value = val;
  }
}

class CheckboxControl extends Rete.Control {
  constructor(emitter, key, label, readonly) {
    super(key);
    this.component = VueCheckboxControl;
    this.props = { emitter, ikey: key, label, readonly };
  }
  setValue(val) {
    this.vueContext.value = val;
  }
}

class InputFileControl extends Rete.Control {
  constructor(emitter, key, label, readonly) {
    super(key);
    this.component = VueInputFileControl;
    this.props = { emitter, ikey: key, label, readonly };
  }
  setValue(val) {
    this.vueContext.value = val;
  }
}

/* 
  Component:
  1. OpenLigandComp
  2. PDBSplitComp
  3. PLANTSBindComp
  4. CombineLigandComp
  5. OpenbabelConvComp
  6. PLANTSDockComp
  7. VINADockComp
  8. SaveDBComp
*/

class OpenLigandComp extends Rete.Component {
  constructor() {
    super("Ligand Input")
    this.path = ["Input"];
  }

  builder(node) {
    var out1 = new Rete.Output("lig1", "Ligand", molSocket);

    return node.addControl(new InputFileControl(this.editor, "lig1", "Ligand")).addOutput(out1);
  }
}

class PDBSplitComp extends Rete.Component {
  constructor() {
    super("PDB Split")
    this.path = ["Input"];
  }

  builder(node) {
    var out1 = new Rete.Output("lig1", "Ligand", molSocket);
    var out2 = new Rete.Output("prot1", "Protein", molSocket);

    return node
      .addControl(new InputFileControl(this.editor, "PDBFile", "PDB File"))
      .addControl(new TextControl(this.editor, "ligID", "Ligand ID"))
      .addOutput(out1)
      .addOutput(out2);
  }
}

class PLANTSBindComp extends Rete.Component {
  constructor() {
    super("PLANTS Binding Site");
    this.path = ["Docking"];
  }

  builder(node) {
    let inLigand = new Rete.Input("inLigand", "Input Ligand", molSocket)
    let outBindDef = new Rete.Output("outBindDef", "Binding site definition", bindDefSocket)

    return node
      .addInput(inLigand)
      .addOutput(outBindDef)
      .addControl(new TextControl(this.editor, "radius", "5", "radius"))
  }
}

class CombineLigandComp extends Rete.Component {
  constructor() {
    super("Combine Ligand");
    this.path = ["Cheminformatics"];
  }

  builder(node) {
    let inLigand1 = new Rete.Input("inLigand1", "Input Ligand 1", molSocket)
    let inLigand2 = new Rete.Input("inLigand2", "Input Ligand 2", molSocket)
    let outLigand = new Rete.Output("outLigand", "Output Ligand", molSocket)

    return node
      .addInput(inLigand1)
      .addInput(inLigand2)
      .addOutput(outLigand)
  }
}

class OpenbabelConvComp extends Rete.Component {
  constructor() {
    super("Openbabel Conversion");
    this.path = ["Cheminformatics"];
    this.inOptions = [
      {value: "", name: "Input Format"},
      {value: "mol2", name: "Mol2"},
      {value: "pdb", name: "PDB"},
      {value: "pdbqt", name: "PDBQT"},
      {value: "smiles", name: "SMILES"}
    ];
    this.outOptions = [
      {value: "", name: "Output Format"},
      {value: "mol2", name: "Mol2"},
      {value: "pdb", name: "PDB"},
      {value: "pdbqt", name: "PDBQT"},
      {value: "smiles", name: "SMILES"}
    ];
  }

  builder(node) {
    let inMol  = new Rete.Input("inMol", "Input Molecule", molSocket);
    let outMol = new Rete.Output("prot", "Output Molecule", molSocket);

    return node
      .addInput(inMol)
      .addOutput(outMol)
      .addControl(new CheckboxControl(this.editor, "gen3D", "gen3D"))
      .addControl(new OptControl(this.editor, "inFormat", this.inOptions))
      .addControl(new OptControl(this.editor, "outFormat", this.outOptions))
  }
}

class PLANTSDockComp extends Rete.Component {
  constructor() {
    super("Docking with PLANTS");
    this.path = ["Docking"];
  }

  builder(node) {
    let inLigand = new Rete.Input("inLigand", "Input Ligand", molSocket);
    let inProtein = new Rete.Input("inProtein", "Input Protein", molSocket);
    let inBindDef = new Rete.Input("inBindDef", "Binding Site Definition", bindDefSocket);
    let outSaveResult = new Rete.Output("outSaveResult", "Docking Result", resultSocket);

    return node
      .addInput(inLigand)
      .addInput(inProtein)
      .addInput(inBindDef)
      .addOutput(outSaveResult)
  }
}

class VINADockComp extends Rete.Component {
  constructor() {
    super("Docking with VINA");
    this.path = ["Docking"];
  }

  builder(node) {
    let inLigand = new Rete.Input("inLigand", "Input Ligand", molSocket);
    let inProtein = new Rete.Input("inProtein", "Input Protein", molSocket);
    let inBindDef = new Rete.Input("inBindDef", "Binding Site Definition", bindDefSocket);
    let outSaveResult = new Rete.Output("outSaveResult", "Docking Result", resultSocket);

    return node
      .addInput(inLigand)
      .addInput(inProtein)
      .addInput(inBindDef)
      .addOutput(outSaveResult)
      .addControl(new TextControl(this.editor, "boxSize", "12", "Box Size"))
  }
}

class SaveDBComp extends Rete.Component {
  constructor() {
    super("Save to Database");
    this.path = ["Output"];
  }

  builder(node) {
    return node.addInput(new Rete.Input("inResult", "Result", resultSocket))
  }
}

class NumComponent extends Rete.Component {
  constructor() {
    super("Number");
    this.path = ["math"];
  }

  builder(node) {
    var out1 = new Rete.Output("num1", "Number", numSocket);

    return node.addControl(new NumControl(this.editor, "num1")).addOutput(out1);
  }
}

class AddComponent extends Rete.Component {
  constructor() {
    super("Add");
    this.path = ["math"];
  }

  builder(node) {
    var inp1 = new Rete.Input("num1", "Number1", numSocket);
    var inp2 = new Rete.Input("num2", "Number2", numSocket);
    var out = new Rete.Output("num3", "Result", numSocket);

    inp1.addControl(new NumControl(this.editor, "num1"));
    inp2.addControl(new NumControl(this.editor, "num2"));

    return node
      .addInput(inp1)
      .addInput(inp2)
      .addControl(new NumControl(this.editor, "preview", true))
      .addOutput(out);
  }
}

class ProtLigandExtractComponent extends Rete.Component {
  constructor() {
    super("Extract Protein Ligand");
    this.path = ["docking"];
    this.options = [
      {value: "mol2", name: "Mol2"},
      {value: "pdb", name: "PDB"},
      {value: "pdbqt", name: "PDBQT"},
      {value: "smiles", name: "SMILES"}
    ];
  }

  builder(node) {
    let outProt = new Rete.Output("prot", "Protein", numSocket);

    return node
      .addOutput(outProt)
      .addControl(new OptControl(this.editor, "options", this.options))
      .addControl(new NumControl(this.editor, "pdb"));
  }
}

export default {
  name: "app",
  data () {
    return {
      workflow: {
        name: 'untitled_workflow'
      }
    }
  },
  async mounted() {
    var container = document.querySelector("#rete");
    var components = [
      new OpenLigandComp(),
      new PDBSplitComp(),
      new OpenbabelConvComp(),
      new CombineLigandComp(),
      new PLANTSBindComp(),
      new PLANTSDockComp(),
      new VINADockComp(),
      new SaveDBComp(),
      // new NumComponent(),
      // new AddComponent(),
      // new ProtLigandExtractComponent()
    ];

    var editor = new Rete.NodeEditor("simulatio@0.1.0", container);
    editor.use(ConnectionPlugin.default);
    editor.use(VueRenderPlugin.default);
    editor.use(ContextMenuPlugin.default, {
      delay: 80,
      items: {
        "Dump JSON": () =>
          saveAs(
            new Blob([JSON.stringify(editor.toJSON(), null, 2)], {
              type: "application/json"
            }),
            "workflow.json"
          )
        //'Dump JSON': () => console.log(JSON.stringify(editor.toJSON()))
      },
      allocate(component) {
        return component.path;
      }
    });
    editor.use(AreaPlugin);
    editor.use(CommentPlugin.default);
    editor.use(HistoryPlugin);
    editor.use(ConnectionMasteryPlugin.default);

    // var engine = new Rete.Engine("simulatio@0.1.0");

    components.map(c => {
      editor.register(c);
      //  engine.register(c);
    });

    /*
    var n1 = await components[2].createNode({ num1: 2 });
    var n2 = await components[2].createNode({ num1: 4 });
    var add = await components[3].createNode();

    n1.position = [80, 200];
    n2.position = [80, 400];
    add.position = [500, 240];

    editor.addNode(n1);
    editor.addNode(n2);
    editor.addNode(add);

    editor.connect(n1.outputs.get("num1"), add.inputs.get("num1"));
    editor.connect(n2.outputs.get("num1"), add.inputs.get("num2"));
    */

    editor.view.resize();
    AreaPlugin.zoomAt(editor);
    editor.trigger("process");
  }
};
</script>
<style>

.btn-sm {
  padding: 5px 5px !important;
  margin: 8px 5px !important;
  width: 95px !important;
}

.form-control {
  font-size: 0.9rem;
}

#rete {
  position: relative;
  overflow: hidden;
  width: 1401px !important;
  height: 801px !important;
  border-radius: 10px;
  stroke-width: 23;
  background: url("/img/grid1.png");
}

.node .control input,
.node .input-control input {
  width: 60px;
}

.context-menu {
  width: 150px !important;
  padding: 0px !important;
  border: 1px solid darkgrey !important;
  border-radius: 6px !important;
  box-shadow: 0 2px 5px 0 rgba(0, 0, 0, 0.2), 0 4px 8px 0 rgba(0, 0, 0, 0.19);
}

.subitems {
  width: 160px !important;
  border: 1px solid darkgrey !important;
  border-radius: 6px !important;
}

.search {
  border-bottom: solid 0.8px rgb(190, 190, 190) !important;
  background-image: linear-gradient(to bottom, #ffffff 0%,#e5e5e5 100%) !important;
  background-repeat: repeat, repeat !important;
  background-position: right .7em top 50%, 0 0 !important;
  background-size: .65em auto, 100% !important;
}

.search input {
  color: gray !important;
  font-size: 92% !important;
  border: 1px solid darkgrey !important;
}

.item {
  color: gray !important;
  border-bottom: solid 1px rgb(190, 190, 190) !important;
  background-image: linear-gradient(to bottom, #ffffff 0%,#e5e5e5 100%) !important;
  background-repeat: repeat, repeat !important;
  background-position: right .7em top 50%, 0 0 !important;
  background-size: .65em auto, 100% !important;
  font-size: 92%;
}

select, input {
  width: 100%;
  border-radius: 4px;
  background-color: white;
  padding: 2px 8px;
  border: 1px solid #999;
  font-size: 92%;
}

.custom-select {
  position: relative;
  font-family: Arial, Helvetica, sans-serif;
}

.custom-select select {
  display: none; /*hide original SELECT element: */
}

.node {
  /* background: #3498db !important; */
  border: 2px solid #3f474da1 !important;
  background-image: linear-gradient(to bottom, #ffffff 0%,#dedede 100%) !important;
  background-repeat: repeat, repeat !important;
  background-position: right .7em top 50%, 0 0 !important;
  background-size: .65em auto, 100% !important;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
}

.node .title {
  border-bottom: solid 1px rgb(151, 151, 151) !important;
  font-size: 16px !important;
  text-align: center;
  font-weight: bold;
  font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  margin-bottom: 8px !important;
  padding: 5px !important;
}

.node.selected {
  border: 2px solid lime !important;
  background-image: linear-gradient(to bottom, #ffffff 0%,#e5e5e5 100%) !important;
  background-repeat: repeat, repeat !important;
  background-position: right .7em top 50%, 0 0 !important;
  background-size: .65em auto, 100% !important;
}

.socket {
  border: 2px solid gainsboro !important;
  width: 18px !important;
  height: 18px !important;
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

.node .title {
  color: gray !important;
  margin: 4px !important;
}

.node .input-title {
  color: gray !important;
  margin: 4px !important;
}

.node .output-title {
  color: gray !important;
  margin: 4px !important;
}

.node .control-title {
  color: gray !important;
  margin: 4px !important;
}

label.control {
  width: 100%;
  /* float: left; */
}

span.controlLabel {
  float: left;
  font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  width: 100%;
  margin-bottom: 5px;
  color: dimgray !important;
}

.connection .main-path {
  stroke-width: 3px !important;
  stroke:cornflowerblue !important;
}

input[type="text"] {
  display: block;
  border-radius: 4px;
  font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  width: 160px !important;
  padding: .3em .5em .4em .6em;
  border: 1px solid #aaa;
  box-shadow: 0 1px 0 1px rgba(0,0,0,.04);
  border-radius: .4em;
  -moz-appearance: textfield;
  background-color: #fff;
  background-image: linear-gradient(to bottom, #ffffff 0%,#efefef 100%);
  background-repeat: repeat, repeat;
  background-position: right .7em top 50%, 0 0;
  background-size: .65em auto, 100%;
}

input[type="file"] {
  display: block;
  border-radius: 4px;
  font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  width: 200px !important;
  padding: .3em .5em .4em .6em;
  border: 1px solid #aaa;
  box-shadow: 0 1px 0 1px rgba(0,0,0,.04);
  border-radius: .4em;
  -moz-appearance: textfield;
  background-color: #fff;
  background-image: linear-gradient(to bottom, #ffffff 0%,#efefef 100%);
  background-repeat: repeat, repeat;
  background-position: right .7em top 50%, 0 0;
  background-size: .65em auto, 100%;
}

input[type="number"] {
  display: block;
  border-radius: 4px;
  font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  width: 180px !important;
  padding: .3em .5em .4em .6em;
  border: 1px solid #aaa;
  box-shadow: 0 1px 0 1px rgba(0,0,0,.04);
  border-radius: .4em;
  -moz-appearance: textfield;
  background-color: #fff;
  background-image: linear-gradient(to bottom, #ffffff 0%,#efefef 100%);
  background-repeat: repeat, repeat;
  background-position: right .7em top 50%, 0 0;
  background-size: .65em auto, 100%;
}

/* Remove spinner from number input for: Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

select {
  display: block;
  border-radius: 4px;
  font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  width: 130px !important;
  padding: .3em .5em .4em .6em;
  border: 1px solid #aaa;
  box-shadow: 0 1px 0 1px rgba(0,0,0,.04);
  border-radius: .4em;
  -moz-appearance: none;
  -webkit-appearance: none;
  appearance: none;
  background-color: #fff;
  background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23007CB2%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'),
    linear-gradient(to bottom, #ffffff 0%,#efefef 100%);
  background-repeat: no-repeat, repeat;
  background-position: right .7em top 50%, 0 0;
  background-size: .65em auto, 100%;
}

.save-result-to-db {
  background: darkviolet !important;
}

.socket-input-save-result-to-db .main-path {
  stroke: darkviolet !important;
}

.molecule-value {
  background:hotpink !important;
}

.socket-input-molecule-value .main-path {
  stroke: hotpink !important;
}

.binding-site-definition {
  background: #999 !important;
}

.socket-input-binding-site-definition .main-path {
  stroke: #999 !important;
}

.frame-comment, .inline-comment {
  color:rgba(0, 0, 0, 0.76) !important;
}
</style>

