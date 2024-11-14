import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

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
        if set(nx.get_node_attributes(self.G, 'label').values()) != label_set:
            return False
        return True

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
        print("Lewa strona transformacji nie jest podzbiorem oryginalnego grafu. Zwracamy oryginalny graf.")
        return m

    # Usuwanie węzłów z grafu początkowego, które nie występują w prawym grafie
    to_delete = []
    for i, label in enumerate(left.labels):
        if label not in [node_data['label'] for _, node_data in right.G.nodes(data=True)]:
            to_delete.append([label, i])

    # Usuwanie węzłów i ich krawędzi
    for i in to_delete:
        for j in range(len(m.labels)):
            if i[0] == m.labels[j]:
                m.G.remove_edges_from(list(m.G.edges(j)))
                m.G.remove_node(j)
                break

    for i in to_delete:
        m.labels[i[1]] = -1

    # Dodawanie nowych węzłów z prawego grafu, które nie istnieją w lewym
    new_nodes = []
    new_labels = []
    for i, label in enumerate(right.labels):
        if label not in [node_data['label'] for _, node_data in m.G.nodes(data=True)]:
            new_nodes.append([label, i])

    # Dodanie nowych węzłów do grafu
    for i in range(len(new_nodes)):
        new_labels.append(new_nodes[i][0])
        m.G.add_node(len(m.labels) + i, label=new_nodes[i][0])

    m.labels = m.labels + new_labels

    # Usuwanie krawędzi, które są w lewym grafie, ale już istnieją w grafie początkowym
    for i in list(left.G.edges):
        a = left.G.nodes[i[0]]['label']
        b = left.G.nodes[i[1]]['label']

        if a in m.labels and b in m.labels and a != -1 and b != -1:
            a1 = m.labels.index(a)
            b1 = m.labels.index(b)
            if (a1, b1) in m.G.edges:
                m.G.remove_edge(a1, b1)

    # Dodawanie krawędzi z prawego grafu, które są w nowym grafie
    for i in list(right.G.edges):
        a = right.G.nodes[i[0]]['label']
        b = right.G.nodes[i[1]]['label']

        if a in m.labels and b in m.labels and a != -1 and b != -1:
            a1 = m.labels.index(a)
            b1 = m.labels.index(b)
            m.G.add_edge(a1, b1)

    return m


def is_subgraph(sub, full):
    sub_labels = [node_data['label'] for _, node_data in sub.G.nodes(data=True)]
    full_labels = [node_data['label'] for _, node_data in full.G.nodes(data=True)]
    
    if not set(sub_labels).issubset(set(full_labels)):
        return False

    for edge in sub.G.edges:
        if edge not in full.G.edges:
            return False

    return True


def draw(graph, filename):
    plt.clf()
    plt.title(filename)
    pos = nx.spring_layout(graph.G)
    labels = nx.get_node_attributes(graph.G, 'label')
    nx.draw_networkx(graph.G, pos, with_labels=True, labels=labels, node_color='lightblue', font_size=10)
    plt.savefig(filename)
    plt.show()

def save_to_excel(graph, file_name='dane_grafu.xlsx'):
    labels = [{"Węzeł": n, "Etykieta": graph.G.nodes[n]['label']} for n in graph.G.nodes()]
    edges = [{"Początek": e[0], "Koniec": e[1]} for e in graph.G.edges()]

    with pd.ExcelWriter(file_name) as writer:
        pd.DataFrame(labels).to_excel(writer, sheet_name='Węzły')
        pd.DataFrame(edges).to_excel(writer, sheet_name='Krawędzie')

def start():
    which_example = input('Wybierz przykład [1, 2, 3, 4, 5]: ')
    if which_example.isdigit() and int(which_example) in [1, 2, 3, 4, 5]:
        graph = Graph.from_file(f"example{which_example}.txt")
        init_graph = graph[0]

        draw(init_graph, 'graf_poczatkowy.png')
        save_to_excel(init_graph, 'dane_graf_poczatkowy.xlsx')

        transformation_count = int((len(graph) - 1) / 2)
        transformation_indexes = [str(i) for i in range(1, transformation_count + 1)]
        transformation_index = int(input(f'Wybierz transformację [{",".join(transformation_indexes)}]: '))

        left = graph[transformation_index * 2 - 1]
        right = graph[transformation_index * 2]

        if input('Narysować lewą stronę transformacji [y/n] :') == 'y':
            draw(left, 'lewa_strona_transformacji.png')
            save_to_excel(left, 'dane_lewa_strona.xlsx')

        if input('Narysować prawą stronę transformacji [y/n] :') == 'y':
            draw(right, 'prawa_strona_transformacji.png')
            save_to_excel(right, 'dane_prawa_strona.xlsx')

        graf_after_transformation = single_push_out(left, right, init_graph)
        draw(graf_after_transformation, 'graf_po_transformacji.png')
        save_to_excel(graf_after_transformation, 'dane_graf_po_transformacji.xlsx')

if __name__ == "__main__":
    start()
