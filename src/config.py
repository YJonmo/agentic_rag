import os


current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(current_dir, "data", "raw")
faq_file = os.path.join(data_dir, "faqs.csv")
prod_occu_file = os.path.join(data_dir, "products_occupation.json")
vec_data_dir = os.path.join(current_dir, "data", "vector")
persistent_directory = os.path.join(vec_data_dir, "db_faq_prod_occu")

