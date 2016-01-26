#!/usr/bin/python
#coding: utf-8

import github3, sys, pymysql.cursors, time, datetime
from multiprocessing.dummy import Pool as ThreadPool

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '[t] %s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

class GitHubKeysScrapper:
    def __init__(self, gh_login, gh_password):
        self.db_connection = self.db_connect()
        self.gh = github3.login(gh_login, password=gh_password)

    def db_connect(self):
        mysql_usr = 'mysql_user'
        mysql_pwd = 'mysql_password'
        mysql_db  = 'mysql_db'

        db_connection = pymysql.connect(
            #host='localhost',
            unix_socket='/var/lib/mysql/mysql.sock',
            user=mysql_usr, password=mysql_pwd, db=mysql_db,
            charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
        )

        return db_connection

    @timing
    def assync_users_proceed(self, users_pool, threads):
        pool = ThreadPool(threads)
        try:
            full_users = pool.map(self.get_user_info, users_pool)
        except Exception, e:
            print e
            full_users = []
        pool.close() 
        pool.join()
        return full_users
    
    def get_user_info(self, user):
        if not user.email:
            user.refresh(True)
        user.keys = list(user.keys())
        return user

    @timing
    def store_users(self, users):
        user_insert = []
        key_insert  = []
        for user in users:
            user_insert_one = (user.id, user.name, user.email, user.login, user.blog)
            user_insert.append(user_insert_one)
            for key_line in user.keys:
                key_type, key = key_line.key.split()
                key_insert_one = (key_type, key, user.id)
                key_insert.append(key_insert_one)

        try:
            with self.db_connection.cursor() as cursor:
                if user_insert:
                    cursor.executemany("INSERT IGNORE INTO `user` (`id`, `name`, `email`, `login`, `site`) VALUES (%s,%s,%s,%s,%s)", user_insert)
                if key_insert:
                    cursor.executemany("INSERT IGNORE INTO `pub_key` (`type`, `pub_key`, `user_id`) VALUES (%s, %s, %s)", key_insert)
            self.db_connection.commit()
        except Exception, e:
            print e
    
    def get_limit(self):
        try:
            return self.gh.ratelimit_remaining
        except Exception, e:
            print e
            return 0

    def get_time(self):
        return datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        
    def unix_to_time(self, unix_time):
        return datetime.datetime.fromtimestamp(unix_time).strftime('%H:%M:%S')

    def sleep_until_reset(self):
        reset_time = self.gh.rate_limit()['resources']['core']['reset'] + 15
        print '[i] (%s) Sleep until %s...' % (self.get_time(), self.unix_to_time(reset_time))
        time.sleep(reset_time - time.time())

    def parse_users(self, since_user_id = None, users_chunk = 50):
        if not self.get_limit():
            self.sleep_until_reset()
        users = self.gh.all_users(since=since_user_id)
        users_pool = []
        users_count = 0
        count = 0
        for user in users:
            sleep = False
            count += 1
            
            print "[*] %d: \t %s" % (user.id, user.login)
            
            if self.get_limit() <= users_chunk * 2:
                users_count += count
                print "[E] Etag: ", users.etag
                print "[+] Users: %d" % (users_count)
                self.sleep_until_reset()

            users_pool.append(user)

            if count >= users_chunk:
                print '[+] %d users reached. %d requests left.' % (users_chunk, self.gh.ratelimit_remaining)
                
                full_users = self.assync_users_proceed(users_pool, users_chunk)
                self.store_users(full_users)

                users_count += count
                users_pool = []
                count = 0


since = sys.argv[1] if len(sys.argv) > 1 else None

GH = GitHubKeysScrapper('username', 'password')
GH.parse_users(users_chunk = 50, since_user_id = since)