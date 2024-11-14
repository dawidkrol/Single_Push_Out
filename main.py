import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

class Graph:
    def __init__(self, labels, edges):
        self.labels = labels  # Lista etykiet węzłów
        self.edges = edges    # Lista krawędzi (par węzłów)
        self.G = nx.Graph()   # Graf z użyciem NetworkX
        for i, label in enumerate(labels):
            self.G.add_node(i, label=label)  # Dodaj węzły z etykietami
        for edge in edges:
            self.G.add_edge(*edge)  # Dodaj krawędzie

    def correct(self):
        # Sprawdza, czy etykiety węzłów w grafie zgadzają się z oryginalnymi etykietami
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
                    # Parsowanie krawędzi
                    edges = [tuple(map(int, edge[1:-1].split(','))) for edge in line.split(";")]
                else:
                    # Parsowanie etykiet węzłów
                    labels = line.split(";")
                    g = cls(labels, edges)
                    if g.correct():
                        graphs.append(g)
            return graphs

def spo(left, right, m):
    # Sprawdzamy, czy lewa strona jest podzbiorem początkowego grafu
    if not is_subgraph(left, m):
        print("Lewa strona transformacji nie jest podzbiorem oryginalnego grafu. Zwracamy oryginalny graf.")
        return m  # Zwracamy oryginalny graf, bez żadnej zmiany

    # Usuwanie węzłów z grafu początkowego, które nie występują w prawym grafie
    to_delete = []
    for i, label in enumerate(left.labels):
        if i not in right.G.nodes:
            to_delete.append([label, i])

    # Usuwanie węzłów i ich krawędzi
    for i in to_delete:
        for j in range(len(m.labels)):
            if i[0] == m.labels[j]:
                m.G.remove_edges_from(list(m.G.edges(j)))  # Usuń wszystkie krawędzie wychodzące z węzła
                m.G.remove_node(j)  # Usuń węzeł
                break

    # Aktualizowanie etykiety węzłów na -1
    for i in to_delete:
        m.labels[i[1]] = -1

    # Dodawanie nowych węzłów z prawego grafu, które nie istnieją w lewym
    new_nodes = []
    new_labels = []
    for i, label in enumerate(right.labels):
        if i not in left.G.nodes:
            new_nodes.append([label, i])

    # Dodanie nowych węzłów do grafu
    for i in range(len(new_nodes)):
        new_labels.append(new_nodes[i][0])
        m.G.add_node(len(m.labels) + i, label=new_nodes[i][0])

    # Aktualizacja etykiet węzłów
    m.labels = m.labels + new_labels

    # Usuwanie krawędzi, które są w lewym grafie, ale już istnieją w grafie początkowym
    for i in list(left.G.edges):
        a = left.labels[i[0]]
        b = left.labels[i[1]]

        if a in m.labels and b in m.labels and a != -1 and b != -1:
            a1 = 0
            b1 = 0
            for j in range(len(m.labels)):
                if m.labels[j] == a:
                    a1 = j
                if m.labels[j] == b:
                    b1 = j
            if (a1, b1) in m.G.edges:
                m.G.remove_edge(a1, b1)

    # Dodawanie krawędzi z prawego grafu, które są w nowym grafie
    for i in list(right.G.edges):
        if len(list(left.G.nodes)) >= len(list(right.G.nodes)):
            a = left.labels[i[0]]
            b = left.labels[i[1]]
        else:
            a = right.labels[i[0]]
            b = right.labels[i[1]]

        if a in m.labels and b in m.labels and a != -1 and b != -1:
            a1 = 0
            b1 = 0
            for j in range(len(m.labels)):
                if m.labels[j] == a:
                    a1 = j
                if m.labels[j] == b:
                    b1 = j
            m.G.add_edge(a1, b1)

    return m

def is_subgraph(sub, full):
    """
    Funkcja sprawdzająca, czy graf 'sub' jest podzbiorem grafu 'full'.
    """
    # Sprawdzamy, czy etykiety węzłów w 'sub' są podzbiorem etykiet w 'full'
    if not set(sub.labels).issubset(set(full.labels)):
        return False

    # Sprawdzamy, czy krawędzie w 'sub' są podzbiorem krawędzi w 'full'
    for edge in sub.G.edges:
        if edge not in full.G.edges:
            return False

    return True

def draw(graph, filename):
    plt.clf()
    plt.title(filename)
    pos = nx.spring_layout(graph.G)  # Używamy obiektu 'G' do obliczenia układu węzłów
    labels = nx.get_node_attributes(graph.G, 'label')
    nx.draw_networkx(graph.G, pos, with_labels=True, labels=labels, node_color='lightblue', font_size=10)
    plt.savefig(filename)  # Zapisz obraz grafu
    plt.show()

def zapisz_do_excela(graph, nazwa_pliku='dane_grafu.xlsx'):
    wezly = [{"Węzeł": n, "Etykieta": graph.G.nodes[n]['label']} for n in graph.G.nodes()]
    krawedzie = [{"Początek": e[0], "Koniec": e[1]} for e in graph.G.edges()]

    with pd.ExcelWriter(nazwa_pliku) as writer:
        pd.DataFrame(wezly).to_excel(writer, sheet_name='Węzły')
        pd.DataFrame(krawedzie).to_excel(writer, sheet_name='Krawędzie')

def start():
    which_example = input('Wybierz przykład [1, 2, 3, 4, 5]: ')
    if which_example.isdigit() and int(which_example) in [1, 2, 3, 4, 5]:
        grafy = Graph.from_file(f"example{which_example}.txt")
        graf_poczatkowy = grafy[0]

        # Rysowanie grafu początkowego
        draw(graf_poczatkowy, 'graf_poczatkowy.png')
        zapisz_do_excela(graf_poczatkowy, 'dane_graf_poczatkowy.xlsx')

        ilosc_transformacji = int((len(grafy) - 1) / 2)
        indeksy_transformacji = [str(i) for i in range(1, ilosc_transformacji + 1)]
        ktora_transformacja = int(input(f'Wybierz transformację [{",".join(indeksy_transformacji)}]: '))

        lewy = grafy[ktora_transformacja * 2 - 1]
        prawy = grafy[ktora_transformacja * 2]

        if input('Narysować lewą stronę transformacji [y/n] :') == 'y':
            draw(lewy, 'lewa_strona_transformacji.png')
            zapisz_do_excela(lewy, 'dane_lewa_strona.xlsx')

        if input('Narysować prawą stronę transformacji [y/n] :') == 'y':
            draw(prawy, 'prawa_strona_transformacji.png')
            zapisz_do_excela(prawy, 'dane_prawa_strona.xlsx')

        graf_po_transformacji = spo(lewy, prawy, graf_poczatkowy)
        draw(graf_po_transformacji, 'graf_po_transformacji.png')
        zapisz_do_excela(graf_po_transformacji, 'dane_graf_po_transformacji.xlsx')

if __name__ == "__main__":
    start()
