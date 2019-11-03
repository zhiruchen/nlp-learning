import math

from collections import defaultdict
import icecream as ic

from bs4 import BeautifulSoup


class Station(object):
    def __init__(self, line, name, lat, lng):
        self.line = line
        self.name = name
        self.lat = lat
        self.lng = lng


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return radius * c


def parse_stations():
    """
    https://blog.csdn.net/GISShiXiSheng/article/details/44976241
    """

    stations = defaultdict(list)

    with open("subway_data.txt") as f:
        data = f.read()
        soup = BeautifulSoup(data, 'lxml')  # Parse the HTML as a string
        table = soup.find_all('table')[0]  # Grab the first table

        line_name = ''
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) == 1:
                line_name = columns[0].get_text()
                stations[line_name] = []
                continue

            if line_name == '':
                continue

            name, lat, lng = columns[1].get_text(), float(columns[3].get_text()), float(columns[4].get_text())
            stations[line_name].append(Station(line_name, name, lat, lng))

    return stations


station_info = {}


def build_station_graph(stations):
    graph = defaultdict(list)
    station_list = stations.values()
    for ss in station_list:
        for i, s in enumerate(ss):
            station_info[s.name] = s

            pre, back = None, None
            if i == 0:
                back = ss[i+1]
            elif i == len(ss)-1:
                pre = ss[i-1]
            else:
                pre, back = ss[i-1], ss[i+1]

            origin = graph[s.name]
            if pre and pre not in origin:
                graph[s.name].append(pre.name)
            if back and back not in origin:
                graph[s.name].append(back.name)

    return graph


def get_station_distance(s1, s2):
    st1, st2 = station_info[s1], station_info[s2]
    return distance((st1.lat, st1.lng), (st2.lat, st2.lng))


def shortest_path(station_graph, src, dest, search_strategy):
    path_list = [[src]]

    while path_list:
        path = path_list.pop(0)
        frontier = path[-1]

        successor = station_graph[frontier]
        for s in successor:
            if s in path:
                continue

            new_path = path + [s]
            path_list.append(new_path)

        path_list = search_strategy(path_list)
        if path_list and path_list[0][-1] == dest:
            return path_list[0]


def get_distance_of_path(path):
    return sum([get_station_distance(path[i], path[i + 1]) for i in range(len(path) - 1)])


def sort_by_distance(path_list):
    return sorted(path_list, key=get_distance_of_path)


def search(station_graph, src, dest):
    print(station_graph)
    path = shortest_path(station_graph, src, dest, sort_by_distance)
    return path


if __name__ == "__main__":
    # ss = defaultdict(list)
    # ss["L1"] = [Station("L1", "s1", 0, 0), Station("L1", "s2", 0, 0), Station("L1", "s3", 0, 0)]
    # ss["L2"] = [Station("L1", "s3", 0, 0), Station("L1", "s4", 0, 0), Station("L1", "s5", 0, 0)]
    # ss["L3"] = [Station("L1", "s6", 0, 0), Station("L1", "s2", 0, 0), Station("L1", "s9", 0, 0)]
    # graph = build_station_graph(ss)
    # print(graph)
    #
    # for item in graph.items():
    #     name, ss = item
    #     print(name, [s.name for s in ss])

    stations = parse_stations()
    graph = build_station_graph(stations)
    path = search(graph, "海淀黄庄", "五道口")
    print(path)
