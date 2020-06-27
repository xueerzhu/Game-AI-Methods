import collections
import pickle
import sys
import random

from matplotlib.pyplot import imread, imsave
import numpy
from numpy import zeros_like


def build_mesh(image, min_feature_size):
    def scan(box):

        x1, x2, y1, y2 = box
        area = (x2 - x1) * (y2 - y1)

        if area < min_feature_size or (image[x1:x2, y1:y2] == 255).all() or (image[x1:x2, y1:y2] == 0).all():

            # this box is simple enough to handle in one node
            if (image[x1:x2, y1:y2] == 255).all():
                return [box], []
            else:
                return [], []

        else:

            # recursively split this big box on the longest dimension
            if x2 - x1 > y2 - y1:

                cut = int(x1 + (x2 - x1) / 2 + 1)
                first_box = (x1, cut, y1, y2)
                second_box = (cut, x2, y1, y2)

                def rank(b): return (b[2], b[3])

                def first_touch(b): return b[1] == cut

                def second_touch(b): return b[0] == cut

            else:

                cut = int(y1 + (y2 - y1) / 2 + 1)
                first_box = (x1, x2, y1, cut)
                second_box = (x1, x2, cut, y2)

                def rank(b): return (b[0], b[1])

                def first_touch(b): return b[3] == cut

                def second_touch(b): return b[2] == cut

            first_boxes, first_edges = scan(first_box)
            second_boxes, second_edges = scan(second_box)

            my_boxes = []
            my_edges = []

            my_boxes.extend([fb for fb in first_boxes if not first_touch(fb)])
            my_boxes.extend(
                [sb for sb in second_boxes if not second_touch(sb)])

            first_touches = sorted(filter(first_touch, first_boxes), key=rank)
            second_touches = sorted(
                filter(second_touch, second_boxes), key=rank)

            first_merges = {}
            second_merges = {}

            while first_touches and second_touches:

                f, s = first_touches[0], second_touches[0]
                rf, rs = rank(f), rank(s)

                if rf == rs:

                    first_touches.pop(0)
                    second_touches.pop(0)
                    merged = (f[0], s[1], f[2], s[3])
                    first_merges[f] = merged
                    second_merges[s] = merged
                    my_boxes.append(merged)

                elif rf[1] < rs[1]:

                    my_boxes.append(first_touches.pop(0))
                    if rf[1] >= rs[0]:
                        my_edges.append((f, s))

                elif rf[1] > rs[1]:

                    my_boxes.append(second_touches.pop(0))
                    if rf[0] <= rs[1]:
                        my_edges.append((f, s))

                else:

                    my_boxes.append(first_touches.pop(0))
                    my_boxes.append(second_touches.pop(0))
                    my_edges.append((f, s))

            my_boxes.extend(first_touches)
            my_boxes.extend(second_touches)

            for a, b in first_edges:
                my_edges.append(
                    (first_merges.get(a, a), first_merges.get(b, b)))

            for a, b in second_edges:
                my_edges.append(
                    (second_merges.get(a, a), second_merges.get(b, b)))

            return my_boxes, my_edges

            # end of scan

    boxes, edges = scan((0, image.shape[0], 0, image.shape[1]))

    adj = collections.defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    mesh = {'boxes': list(adj.keys()), 'adj': dict(adj)}

    return mesh


if __name__ == '__main__':

    min_feature_size = 16
    filename = None

    if len(sys.argv) == 2:
        filename = sys.argv[1]
    elif len(sys.argv) == 3:
        filename = sys.argv[1]
        min_feature_size = int(sys.argv[2])
    else:
        print("usage: %s map_filename min_feature_size" % sys.argv[0])
        sys.exit(-1)

    img = (imread(filename) * 255).astype(dtype=numpy.uint8)
    if len(img.shape) > 2:
        img = img[:, :, 0]

    mesh = build_mesh(img, min_feature_size)

    print(type(mesh))
    print(mesh.keys())

    with open(filename + '.mesh.pickle', 'wb') as f:
        pickle.dump(mesh, f, protocol=pickle.HIGHEST_PROTOCOL)

    atlas = zeros_like(img)
    for x1, x2, y1, y2 in mesh['boxes']:
        atlas[x1:x2, y1:y2] = random.randint(64, 255)

    imsave(filename + '.mesh.png', atlas)

    print("Built a mesh with %d boxes." % len(mesh['boxes']))
