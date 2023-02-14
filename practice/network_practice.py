import networkx as nx
import matplotlib.pyplot as plt



def get_checking():
    GAll=nx.Graph()
    GAll.add_node('apple')
    GAll.add_node('mango')
    GAll.add_node('grape')
    GAll.add_node('banana')

    GAll.add_edge('apple','mango',weight=1)
    GAll.add_edge('apple','banana',weight=1)
    nx.draw(GAll)
    plt.show()

    print(GAll.edges())
    if nx.has_path(GAll,'apple','grape'):
        length=nx.shortest_path_length(GAll,'apple','grape',weight='wieght')
        print(length)
    else:
        print(int())
    return 0



if __name__=="__main__":
    get_checking()