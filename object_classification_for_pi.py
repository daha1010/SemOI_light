from collections import namedtuple
from handleDetectorIDs import HandleDetectorIDs
from semanticCaller import callSemantic


# from runDetection import aiy_detect

# modifies the classification results to match the semantic api


def html_list(ls):
    return "<br>".join(ls)


def seperate_objects(raw_file):
    result = []  # stores modified data
    element = raw_file[0]
    number_of_detected_elements = element.count(',') + 1
    split = element.rsplit(",")
    for item in split:
        entity = item[0:item.find('(') - 1]
        if entity[0] == ' ':
            entity = entity[1:]
        entity = entity.capitalize()
        if '/' in entity: # removes redundant classification results
            entity_split = entity.rsplit("/")
            entity = entity_split[0]
        score = float(item[item.find('(') + 1:item.find(')')])
        result.append([entity, score, [521.0, 391.0, 20.0, 90.0]]) # just a placeholder because this feature is not usable with the classification

    #print(str(result))
    return result


def run_semantic(classification_results):

    ls_result = seperate_objects(classification_results)
    ls_spliced = []  # stores converted format
    #print(str(ls_result))

    image_dimension_tuple = namedtuple("ImageDimensions", ["width", "height", "size"])
    dimension = image_dimension_tuple(670, 504, 670 * 504)
    image_width = float(dimension.width)  # calculates position
    image_height = float(dimension.height)
    float_size = float(dimension.size)

    max_len = len(ls_result)
    for item in range(0, max_len):
        image_box_tuple = namedtuple("ImageDetectionBox", ["x1", "y1", "x2", "y2"])
        rel_position = ls_result[item][2]
        position = image_box_tuple(rel_position[1] * image_width, rel_position[0] * image_height,
                                   rel_position[3] * image_width, rel_position[2] * image_height)
        covered_area = (position.x2 - position.x1) * (position.y2 - position.y1)
        importance = covered_area / float_size

        entity = ls_result[item][0]
        conf_score = ls_result[item][1]

        ids = HandleDetectorIDs()

        test = ids.kv.get(entity)
        if ids.kv.get(entity) is None:
            ls_spliced.append((entity, conf_score, position, importance, 'not_found')) # if no matching ids were found
        else:
            ls_spliced.append((entity, conf_score, position, importance, ids.kv.get(entity)))

        #print(str(ls_spliced)) 

    # Get Scenes from the SemanticAPI
    semantic = callSemantic()
    semanticResults = semantic.semanticCaller(ls_spliced)

    # Convert the List to display in the Output Field
    semantic_list_html = html_list(semanticResults)
    # print("semantic list", semantic_list_html)
    return semantic_list_html
