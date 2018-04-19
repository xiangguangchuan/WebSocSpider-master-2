import json

tree = {'message':[{'parent_tag':'',
                    'children_tags':[{'child_tag':'',
                                      'detail':[{'num':'','name':''
                                                 }]
                                         ,}]
                    }]}

# tree["message"]["parent_tag"] = "web服务器"
# tree["message"]["parent_tag"]["children_tags"]["child_tag"] = "IIL"

print(tree["message"][0]["children_tags"])

