import re
def validateCredentials(email,username,password):
        alphabets='abcdefghijklmnopqrstuvwxyz'
        numbers='0123456789'
        sp_char='_.'
        email_pattern = re.compile(
        r"^(?=.{1,256})(?=.{1,64}@.{1,255})([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$")
        if not email_pattern.match(email):
            raise Exception(f"Invalid email address: {email}")
        alpha_flag_u,alpha_flag,number_flag,spchar_flag=[False]*4
        for i in username:
            if i in alphabets:
                alpha_flag_u=True
        if(alpha_flag_u):
            pass
        else:
            raise Exception('Invalid User Name! Username contains alphabets.')
        for i in password:
                if i in alphabets:
                    alpha_flag=True
                elif i in numbers:
                    number_flag=True
                elif i in sp_char:
                    spchar_flag=True
        if(alpha_flag and number_flag and spchar_flag):
                pass
        else:
                raise Exception('Invalid Password! it should be mixture of alphabet,digits,speial characters(_.)')