SELECT admin,
       npwp,
       kpp,
       cabang,
       nama,
       kdmap,
       kdbayar,
       masa,
       tahun,
       tanggalbayar,
       bulanbayar,
       tahunbayar,
       datebayar,
       nominal,
       ntpn,
       bank,
       nosk,
       nospm,
       tipe,
       source,
       extra,
       billing,
       nop,
       pembuat,
       CASE
         WHEN SOURCE = 1 THEN 'MPN'
         ELSE 'SPM'
       END AS ket
FROM MPN
WHERE (tahunbayar) = '2021'
UNION ALL
SELECT admin,
       npwp,
       kpp,
       cabang,
       '',
       kdmap,
       '',
       '',
       '',
       DAY(tanggal) AS TANGGALBAYAR,
       BULAN,
       TAHUN,
       tanggal,
       NOMINAL*-1,
       '',
       '',
       '',
       '',
       '',
       3 AS SOURCE,
       '',
       '',
       '',
       '',
       'SPMKP' AS ''
FROM spmkp
WHERE (TAHUN) = '2021'
UNION ALL
SELECT A.admin,
       A.npwp,
       A.kpp,
       A.cabang,
       A.nama,
       kdmap,
       kdbayar,
       masapajak,
       tahunpajak,
       DAY(TANGGALDOC) AS TANGGALBAYAR,
       MONTH(TANGGALDOC) BULAN,
       YEAR(TANGGALDOC) TAHUN,
       TANGGALDOC,
       NOMINAL*-1,
       ntpn,
       '',
       nopbk,
       '',
       '',
       4 AS SOURCE,
       '',
       '',
       '',
       '',
       'PBK KIRIM' AS ''
FROM PBK A
  INNER JOIN MASTERFILE B ON A.NPWP = B.NPWP
WHERE YEAR(TANGGALDOC) = '2021'
AND   A.KPP = B.KPP
AND   A.CABANG = B.CABANG
UNION ALL
SELECT A.ADMIN,
       npwp2,
       kpp2,
       cabang2,
       nama2,
       kdmap2,
       kdbayar2,
       masapajak2,
       tahunpajak2,
       DAY(TANGGALDOC) AS TANGGALBAYAR,
       MONTH(TANGGALDOC) BULAN,
       YEAR(TANGGALDOC) TAHUN,
       TANGGALDOC,
       NOMINAL,
       ntpn,
       '',
       nopbk,
       '',
       '',
       5 AS SOURCE,
       '',
       '',
       '',
       '',
       'PBK TERIMA' AS ''
FROM PBK A
  INNER JOIN MASTERFILE B ON A.NPWP2 = B.NPWP
WHERE YEAR(TANGGALDOC) = '2021'
AND   A.KPP2 = B.KPP
AND   A.CABANG2 = B.CABANG;

select *
from mpn
where tahunbayar ='2021';

select *
from pegawai;

select *
from seksi;

SELECT A.NPWP,
       A.KPP,
       A.CABANG,
       A.NAMA,
       A.KDMAP,
       A.KDBAYAR,
       MASA,
       A.TAHUN,
       TAHUNBAYAR,
       BULANBAYAR,
       DATEBAYAR,
       NOMINAL,
       CASE
         WHEN SUBSTRING(A.KDMAP,1,5) IN ('41131','41111') THEN 'PPM'
         WHEN TAHUNBAYAR = A.TAHUN THEN 'PPM'
         WHEN TAHUNBAYAR - A.TAHUN IN (0,1) AND A.KDMAP IN ('411125','411126') AND A.KDBAYAR IN ('200','199','310','320','390','500','501') THEN 'PPM'
         WHEN (TAHUNBAYAR - A.TAHUN IN (0,1) AND MASA = 12) THEN 'PPM'
         WHEN A.TAHUN > TAHUNBAYAR THEN 'PPM'
         ELSE 'PKM'
       END FLAG_PPM_PKM,
       NIPPJ,
       ntpn,
       nosk,
       E.SEKTOR,
       URAIAN,
       F.NAMA AS NAMA_KLU,
       F.SEKTOR AS SEKTOR_KLU
FROM MPN A
  LEFT JOIN WP B
         ON A.NPWP = B.NPWP
        AND A.KPP = B.KPP
        AND A.CABANG = B.CABANG
  LEFT JOIN MAP E
         ON A.KDMAP = E.KDMAP
        AND A.KDBAYAR = E.KDBAYAR
  LEFT JOIN KLU F ON B.KLU = F.KODE
WHERE TAHUNBAYAR = 2021;

SELECT NIP,
       NAMA_AR,
       NAMA_SEKSI,
       SUM(TARGET_AR) TARGET_JAN_DES,       SUM(NOMINAL) REALISASI_JAN_DES,
       (SUM(NOMINAL)/SUM(TARGET_AR))*100 CAPAIAN,
       SUM(CASE WHEN BULAN BETWEEN 1 AND 6 THEN NOMINAL END) REALISASI_JAN_JUN,
       SUM(CASE WHEN BULAN = 7 THEN TARGET_AR END) TARGET_JUL,
       SUM(CASE WHEN BULAN = 8 THEN TARGET_AR END) TARGET_AGU,
       SUM(CASE WHEN BULAN = 9 THEN TARGET_AR END) TARGET_SEP,
       SUM(CASE WHEN BULAN = 10 THEN TARGET_AR END) TARGET_OKT,
       SUM(CASE WHEN BULAN = 11 THEN TARGET_AR END) TARGET_NOV,
       SUM(CASE WHEN BULAN = 12 THEN TARGET_AR END) TARGET_DES,
       SUM(CASE WHEN BULAN = 7 THEN NOMINAL END) REALISASI_JUL,
       SUM(CASE WHEN BULAN = 8 THEN NOMINAL END) REALISASI_AGU,
       SUM(CASE WHEN BULAN = 9 THEN NOMINAL END) REALISASI_SEP,
       SUM(CASE WHEN BULAN = 10 THEN NOMINAL END) REALISASI_OKT,
       SUM(CASE WHEN BULAN = 11 THEN NOMINAL END) REALISASI_NOV,
       SUM(CASE WHEN BULAN = 12 THEN NOMINAL END) REALISASI_DES
       FROM (SELECT A.NIP,
                    A.NAMA AS NAMA_AR,
                    B.NAMA AS NAMA_SEKSI,
                    C.BULAN,
                    TARGET_AR,
                    NOMINAL
             FROM PEGAWAI A
               LEFT JOIN SEKSI B ON A.SEKSI = B.ID
               LEFT JOIN (SELECT NIP,
                                 TAHUN,
                                 BULAN,
                                 SUM(TARGET) TARGET_AR
                          FROM RENPEN
                          GROUP BY NIP,
                                   TAHUN,
                                   BULAN) C
                      ON A.NIP = C.NIP
                     AND C.TAHUN = 2021
               LEFT JOIN (SELECT NIPPJ,
                                 BULANBAYAR,
                                 SUM(NOMINAL) NOMINAL
                          FROM MPN A
                            LEFT JOIN WP B
                                   ON A.NPWP = B.NPWP
                                  AND A.KPP = B.KPP
                                  AND A.CABANG = B.CABANG
                          WHERE TAHUNBAYAR = 2021
                          GROUP BY 1,
                                   2) D
                      ON C.NIP = D.NIPPJ
                     AND C.BULAN = D.BULANBAYAR
             WHERE JABATAN = 5) Z
GROUP BY 1,
         2,
         3
ORDER BY NAMA_SEKSI ASC;

Select *
from users;
