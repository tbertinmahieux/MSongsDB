// parts taken from:
// http://www.sqlite.org/quickstart.html
// compile with:
// g++ -o c_example2 -lsqlite3 c_example2.c


#include <stdio.h>
#include <sqlite3.h>
#include <stdlib.h>
#include <string.h>
using namespace std;

static int callback(void *NotUsed, int argc, char **argv, char **azColName){
  int i;
  for(i=0; i<argc; i++){
    printf("%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
  }
  printf("\n");
  return 0;
}

int main(int argc, char **argv){
  sqlite3 *db;
  char *zErrMsg = 0;
  int rc;

  // open
  rc = sqlite3_open("testbig.db", &db);
  if( rc ){
    fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    exit(1);
  }

  // begin transaction
  const char* sqlbegin = "BEGIN TRANSACTION";
  rc = sqlite3_exec(db, sqlbegin, callback, 0, &zErrMsg);
  if( rc!=SQLITE_OK ){
	fprintf(stderr, "SQL error: %s\n", zErrMsg);
	sqlite3_free(zErrMsg);
  }

  // add songs
  for (int i = 0; i < 9000000; i++)
    {
      const char* sqlcmd = "insert into songs values('testing','onetwo',3)";
      rc = sqlite3_exec(db, sqlcmd, callback, 0, &zErrMsg);
      if( rc!=SQLITE_OK ){
	fprintf(stderr, "SQL error: %s\n", zErrMsg);
	sqlite3_free(zErrMsg);
      }
    }

  // close transaction
  const char* sqlcommit = "COMMIT";
  rc = sqlite3_exec(db, sqlcommit, callback, 0, &zErrMsg);
  if( rc!=SQLITE_OK ){
    fprintf(stderr, "SQL error: %s\n", zErrMsg);
    sqlite3_free(zErrMsg);
  }

  // close
  sqlite3_close(db);
  return 0;
}
