m00 = 'Description: \n' \
      'Checking a key-check value by an original key and a KCV\n\n' \
      'Please, insert key and KCV.'

m01 = 'Description: \n' \
      '      Decrypt key by master key and a mode.\n\n' \
      '  Rules: \n' \
      '     1) Master key must be 16 bytes; \n' \
      '     2) Encrypted key must be 16 or 24 bytes; \n' \
      '     3) Mode supports only values 0 for ECB and 1 for CBC,' \
      'an another value raised an exception;\n' \
      '        * if CBC mode is chosen then IV must be inputed; \n' \
      '        * if ECB mode is chosen then IV will be ignored; \n' \
      '     4) IV must be 8 bytes; \n' \
      '     5) Decrypting algorithm is 3DES. \n\n' \
      '  Tips: \n' \
      '     It can be used for decrypting DEK (24 bytes) ' \
      'or TPK (16 bytes) by TMK. \n\n' \
      '  Insert master key, encrypted key, mode and IV in hexadecimal...'

menu_dict = {
            0: {
                'label': '> Decrypt key by master',
                'message': m01
                },
            1: {
                'label': '> Exit',
                'message': 'Just exit'
                }
            }
