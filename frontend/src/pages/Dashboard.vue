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

class NumComponent extends Rete.Component {
  constructor() {
    super("Number");
    this.path = ["math"];
  }

  builder(node) {
    var out1 = new Rete.Output("num", "Number", numSocket);

    return node.addControl(new NumControl(this.editor, "num")).addOutput(out1);
  }

  worker(node, inputs, outputs) {
    outputs["num"] = node.data.num;
  }
}

class AddComponent extends Rete.Component {
  constructor() {
    super("Add");
    this.path = ["math"];
  }

  builder(node) {
    var inp1 = new Rete.Input("num", "Number", numSocket);
    var inp2 = new Rete.Input("num2", "Number2", numSocket);
    var out = new Rete.Output("num", "Number", numSocket);

    inp1.addControl(new NumControl(this.editor, "num"));
    inp2.addControl(new NumControl(this.editor, "num2"));

    return node
      .addInput(inp1)
      .addInput(inp2)
      .addControl(new NumControl(this.editor, "preview", true))
      .addOutput(out);
  }

  worker(node, inputs, outputs) {
    var n1 = inputs["num"].length ? inputs["num"][0] : node.data.num1;
    var n2 = inputs["num2"].length ? inputs["num2"][0] : node.data.num2;
    var sum = n1 + n2;

    this.editor.nodes
      .find(n => n.id == node.id)
      .controls.get("preview")
      .setValue(sum);
    outputs["num"] = sum;
  }
}

class ProtLigandExtractComponent extends Rete.Component {
  constructor() {
    super("Extract Protein Ligand");
    this.path = ["docking"];
  }

  builder(node) {
    let outProt = new Rete.Output("prot", "Protein", numSocket);

    return node
      .addOutput(outProt)
      .addControl(new NumControl(this.editor, "pdb"));
  }
  /*
    worker(node, inputs, outputs) {
      outputs['num'] = node.data.num;
    } */
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
      allocate(component) {
        return component.path;
      }
    });
    editor.use(AreaPlugin);
    editor.use(CommentPlugin.default);
    editor.use(HistoryPlugin);
    editor.use(ConnectionMasteryPlugin.default);

    var engine = new Rete.Engine("workflow@0.1.0");

    components.map(c => {
      editor.register(c);
      engine.register(c);
    });

    var n1 = await components[0].createNode({ num: 2 });
    var n2 = await components[0].createNode({ num: 0 });
    var add = await components[1].createNode();

    n1.position = [80, 200];
    n2.position = [80, 400];
    add.position = [500, 240];

    editor.addNode(n1);
    editor.addNode(n2);
    editor.addNode(add);

    editor.connect(n1.outputs.get("num"), add.inputs.get("num"));
    editor.connect(n2.outputs.get("num"), add.inputs.get("num2"));

    editor.on(
      "process nodecreated noderemoved connectioncreated connectionremoved",
      async () => {
        console.log(
          "process"
        ); /*
          console.log(n1);
          console.log(n2);*/
        console.log(editor.toJSON());
        await engine.abort();
        await engine.process(editor.toJSON());
      }
    );

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
}

.subitems {
  width: 200px !important;
}

select,
input {
  width: 100%;
  border-radius: 30px;
  background-color: white;
  padding: 2px 8px;
  border: 1px solid #999;
  font-size: 110%;
  width: 170px;
}

.node {
  background: #3498db !important;
  border: 2px solid #2980b9a1 !important;
}

.node .title {
  border-bottom: solid 1px wheat !important;
  font-size: 16px !important;
  text-align: center;
  font-weight: bold;
  font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  margin-bottom: 8px !important;
  padding: 5px !important;
}

.node.selected {
  background: rgba(120, 180, 80, 0.9) !important;
}

.socket {
  width: 20px !important;
  height: 20px !important;
}

.input-title {
  margin: 4px !important;
}

.output-title {
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
  color: white;
}

input[type="text"] {
  border-radius: 4px;
  font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  width: 180px !important;
  border: solid 1px gainsboro;
}

input[type="number"] {
  border-radius: 4px;
  font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  width: 180px !important;
  border: solid 1px gainsboro;
}
</style>
