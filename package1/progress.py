def progress_function(BTAddress, result):
    if (result ==  1):
        print("Trying BT address: " + BTAddress )
    if (result == 2):
        print ("Done: " + BTAddress )
    #    print (dir(BTAddress))  # prints all the methods of the object
    return 0