import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import copy

class Graph:
    def __init__(self, labels, edges):
        self.labels = labels
        self.edges = edges
        self.G = nx.Graph()
        for i, label in enumerate(labels):
            self.G.add_node(i, label=label)
        for edge in edges:
            self.G.add_edge(*edge)

    def correct(self):
        label_set = {label for label in self.labels}
        return set(nx.get_node_attributes(self.G, 'label').values()) == label_set

    @classmethod
    def from_file(cls, filepath):
        graphs = []
        with open(filepath, "r") as f:
            lines = f.readlines()
            edges = []
            labels = []
            for line in lines:
                line = line.strip()
                if line.startswith("("):
                    edges = [tuple(map(int, edge[1:-1].split(','))) for edge in line.split(";")]
                else:
                    labels = line.split(";")
                    g = cls(labels, edges)
                    if g.correct():
                        graphs.append(g)
            return graphs

def single_push_out(left, right, m):
    if not is_subgraph(left, m):
        print("The left transformation graph is not a subset of the initial graph. Returning the original graph.")
        return m

    to_delete = []
    for i, label in enumerate(left.labels):
        if label not in [node_data['label'] for _, node_data in right.G.nodes(data=True)]:
            to_delete.append([label, i])

    for i in to_delete:
        label_to_remove, index_to_remove = i
        for node in list(m.G.nodes):
            if m.G.nodes[node]['label'] == label_to_remove:
                m.G.remove_edges_from(list(m.G.edges(node)))
                break

    for i in to_delete:
        m.labels[i[1]] = -1

    new_nodes = []
    new_labels = []

    for i, label in enumerate(right.labels):
        if label not in [node_data['label'] for _, node_data in m.G.nodes(data=True)]:
            new_nodes.append([label, i])

    for i in range(len(new_nodes)):
        label = new_nodes[i][0]
        new_labels.append(label)
        if label not in m.labels:
            new_node_index = len(m.labels)
            m.G.add_node(new_node_index, label=label)
            m.labels.append(label)  
            
    for i in list(left.G.edges):
        a = left.G.nodes[i[0]]['label']
        b = left.G.nodes[i[1]]['label']
        if a in m.labels and b in m.labels and a != -1 and b != -1:
            a1 = m.labels.index(a)
            b1 = m.labels.index(b)

            if (a1, b1) in m.G.edges:
                m.G.remove_edge(a1, b1)

    for i in list(right.G.edges):
        a = right.G.nodes[i[0]]['label']
        b = right.G.nodes[i[1]]['label']
        if a in m.labels and b in m.labels and a != -1 and b != -1:
            a1 = m.labels.index(a)
            b1 = m.labels.index(b)

            if (a1, b1) not in m.G.edges and (b1, a1) not in m.G.edges:
                m.G.add_edge(a1, b1)

    return m

def is_subgraph(sub, full):
    sub_labels = {node: data['label'] for node, data in sub.G.nodes(data=True)}
    full_labels = {node: data['label'] for node, data in full.G.nodes(data=True)}

    sub_to_full_mapping = {}
    for sub_node, sub_label in sub_labels.items():
        matched_nodes = [node for node, label in full_labels.items() if label == sub_label]
        if not matched_nodes:
            return False

        sub_to_full_mapping[sub_node] = matched_nodes[0]

    for sub_edge in sub.G.edges:
        u, v = sub_edge
        full_u = sub_to_full_mapping[u]
        full_v = sub_to_full_mapping[v]
        if {full_u, full_v} not in [{edge[0], edge[1]} for edge in full.G.edges]:
            return False

    return True


def draw(graph, title):
    plt.clf()
    plt.title(title)
    pos = nx.spring_layout(graph.G)
    labels = nx.get_node_attributes(graph.G, 'label')
    nx.draw_networkx(graph.G, pos, with_labels=True, labels=labels, node_color='lightblue', font_size=10)
    plt.show()
    
def draw_full_transformation(original_graph, left_graph, right_graph, transformed_graph):
    fig, axs = plt.subplots(2, 2, figsize=(14, 12))

    pos_original = nx.spring_layout(original_graph.G)
    labels_original = nx.get_node_attributes(original_graph.G, 'label')
    nx.draw_networkx(original_graph.G, pos=pos_original, ax=axs[0, 0], with_labels=True, labels=labels_original, node_color='lightgreen', font_size=10)
    axs[0, 0].set_title("Original Graph")

    pos_left = nx.spring_layout(left_graph.G)
    labels_left = nx.get_node_attributes(left_graph.G, 'label')
    nx.draw_networkx(left_graph.G, pos=pos_left, ax=axs[1, 0], with_labels=True, labels=labels_left, node_color='lightcoral', font_size=10)
    axs[1, 0].set_title("Left Transformation Graph")

    pos_right = nx.spring_layout(right_graph.G)
    labels_right = nx.get_node_attributes(right_graph.G, 'label')
    nx.draw_networkx(right_graph.G, pos=pos_right, ax=axs[1, 1], with_labels=True, labels=labels_right, node_color='lightblue', font_size=10)
    axs[1, 1].set_title("Right Transformation Graph")

    pos_transformed = nx.spring_layout(transformed_graph.G)
    labels_transformed = nx.get_node_attributes(transformed_graph.G, 'label')
    nx.draw_networkx(transformed_graph.G, pos=pos_transformed, ax=axs[0, 1], with_labels=True, labels=labels_transformed, node_color='lightyellow', font_size=10)
    axs[0, 1].set_title("Transformed Graph")

    fig.text(0.5, 0.25, '⇒', ha='center', va='center', fontsize=30, color="grey", fontweight="bold")

    fig.text(0.5, 0.75, '⇒', ha='center', va='center', fontsize=30, color="grey", fontweight="bold")
    
    plt.tight_layout()
    plt.show()

def save_to_excel(graph, file_name='graph_data.xlsx'):
    labels = [{"Node": n, "Label": graph.G.nodes[n]['label']} for n in graph.G.nodes()]
    edges = [{"Start": e[0], "End": e[1]} for e in graph.G.edges()]
    with pd.ExcelWriter(file_name) as writer:
        pd.DataFrame(labels).to_excel(writer, sheet_name='Nodes')
        pd.DataFrame(edges).to_excel(writer, sheet_name='Edges')

import copy

def start():
    print("\n--- Graph Transformation Program ---")
    example = input('Choose an example [1, 2]: ')
    if example.isdigit() and int(example) in [1, 2]:
        graph = Graph.from_file(f"example{example}.txt")
        init_graph = graph[0]
        print("\nDisplaying initial graph...")
        draw(init_graph, 'Initial Graph')
        
        save_choice = input("Would you like to save this graph to Excel? (y/n): ").strip().lower()
        if save_choice == 'y':
            save_to_excel(init_graph, 'initial_graph_data.xlsx')
            print("Initial graph saved as 'initial_graph_data.xlsx'")
        
        transformation_count = int((len(graph) - 1) / 2)
        print(f"Available transformations: {list(range(1, transformation_count + 1))}")
        transformation_index = int(input(f'Choose a transformation [1-{transformation_count}]: '))

        left = graph[transformation_index * 2 - 1]
        right = graph[transformation_index * 2]
        
        init_graph_copy = copy.deepcopy(init_graph)
        transformed_graph = single_push_out(left, right, init_graph_copy)
        
        print("\nDisplaying transformation process with original, left, right, and transformed graphs...")
        draw_full_transformation(init_graph, left, right, transformed_graph)

        if input("Would you like to save the transformed graph? (y/n): ").strip().lower() == 'y':
            save_to_excel(transformed_graph, 'transformed_graph_data.xlsx')
            print("Transformed graph saved as 'transformed_graph_data.xlsx'")


if __name__ == "__main__":
    start()
