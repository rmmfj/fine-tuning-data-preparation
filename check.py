import pandas as pd

items_with_label = pd.read_csv("~/Downloads/codingdata/items_with_label.csv")
failed = pd.read_csv("~/Downloads/codingdata/failed_items.csv")
items = pd.read_csv("~/Downloads/codingdata/item.csv")

print("number of rows in items_with_label:", items_with_label.shape[0])
print("every row in items_with_label is unique:", items_with_label['item_id'].is_unique)
print("number of rows in failed items:", failed.shape[0])
print("every row in failed items is unique:", failed['item_id'].is_unique)
print("number of rows in items:", items.shape[0])
print("every row in items is unique:", items['item_id'].is_unique)
