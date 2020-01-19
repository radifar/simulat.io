<template>
  <div>
    <div class="row">
      <div class="col-12">
        <div id="rete" class="node-editor">
          <base-button
            type="success"
            size="sm"
            style="position: absolute; transform: translate(20px, 15px);"
          >Load</base-button>
          <base-button
            type="success"
            size="sm"
            style="position: absolute; transform: translate(90px, 15px);"
          >Save</base-button>
          <base-button
            type="success"
            size="sm"
            style="position: absolute; transform: translate(160px, 15px);"
          >Run</base-button>
        </div>
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

var numSocket = new Rete.Socket("Number value");

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

class OptControl extends Rete.Control {
  constructor(emitter, key, options, readonly) {
    super(key);
    this.component = VueOptControl;
    this.props = { emitter, ikey: key, options: options, readonly };
  }
  setValue(val) {
    this.vueContext.value = val;
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
  async mounted() {
    var container = document.querySelector("#rete");
    var components = [
      new NumComponent(),
      new AddComponent(),
      new ProtLigandExtractComponent()
    ];

    var editor = new Rete.NodeEditor("workflow@0.1.0", container);
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

    // var engine = new Rete.Engine("workflow@0.1.0");

    components.map(c => {
      editor.register(c);
      //  engine.register(c);
    });

    var n1 = await components[0].createNode({ num1: 2 });
    var n2 = await components[0].createNode({ num1: 4 });
    var add = await components[1].createNode();

    n1.position = [80, 200];
    n2.position = [80, 400];
    add.position = [500, 240];

    editor.addNode(n1);
    editor.addNode(n2);
    editor.addNode(add);

    editor.connect(n1.outputs.get("num1"), add.inputs.get("num1"));
    editor.connect(n2.outputs.get("num1"), add.inputs.get("num2"));

    /*
    editor.on(
      "process nodecreated noderemoved connectioncreated connectionremoved",
      async () => {
        console.log(
          "process"
        );
          console.log(n1);
          console.log(n2);
        //console.log(editor.toJSON());
        await engine.abort();
        await engine.process(editor.toJSON());
      }
    );*/

    editor.view.resize();
    AreaPlugin.zoomAt(editor);
    editor.trigger("process");
  }
};
</script>
<style>
#rete {
  position: relative;
  overflow: hidden;
  width: 1401px !important;
  height: 801px !important;
  border-radius: 10px;
  stroke-width: 23;
  /* background was downloaded from hwww.subtlepatterns.com  */
  background: url("/img/grid1.png");
}

.node .control input,
.node .input-control input {
  width: 140px;
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
  border: 1.5px solid gainsboro !important;
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
  border-radius: 4px;
  font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  width: 180px !important;
  border: solid 1px gainsboro;
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
  width: 180px !important;
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
</style>

