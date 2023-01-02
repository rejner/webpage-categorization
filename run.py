from webcat.worker import WebCatWorker



if __name__ == "__main__":
    worker = WebCatWorker()
    # worker.process([
    #         "data/abraxas-forums/abraxas-forums/2015-07-04/index.php_action=recent;start=10",
    #     ])
    worker.process_batch([
        "/workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-11-05/viewtopic.php_pid=4282",
        # "data/abraxas-forums/abraxas-forums/2015-07-04/index.php_action=recent;start=10",
    ])


