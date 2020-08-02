def log_download_progression(page_number, num_of_pages):
    page = 'page'
    if page_number > 1:
        page = 'pages'
    print(f"📄 {page_number} {page} saved out of {num_of_pages}.")
