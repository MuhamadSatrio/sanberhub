-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 21 Jul 2023 pada 17.38
-- Versi server: 10.4.20-MariaDB
-- Versi PHP: 8.0.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `maxxi`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `divisi`
--

CREATE TABLE `divisi` (
  `id` int(11) NOT NULL,
  `divisi` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data untuk tabel `divisi`
--

INSERT INTO `divisi` (`id`, `divisi`) VALUES
(1, 'Pemasaran'),
(2, 'IT');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pegawai`
--

CREATE TABLE `pegawai` (
  `nomor_pegawai` int(11) NOT NULL,
  `nama` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `no_hp` varchar(15) NOT NULL,
  `alamat` varchar(256) NOT NULL,
  `id_divisi` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data untuk tabel `pegawai`
--

INSERT INTO `pegawai` (`nomor_pegawai`, `nama`, `email`, `no_hp`, `alamat`, `id_divisi`) VALUES
(2, 'Satrio2', 'haha@gmail.com', '00812121212', 'dua', 2),
(3, 'Ajeng', 'ajeng@gmail.com', '081212121212', 'Jakarta Pusat', 1),
(12, 'tes1', 'tes@gmail.com', '087855670334', 'fdfsfsdfdsf', 2);

-- --------------------------------------------------------

--
-- Struktur dari tabel `user`
--

CREATE TABLE `user` (
  `id_user` int(11) NOT NULL,
  `email` varchar(128) NOT NULL,
  `password` varchar(256) NOT NULL,
  `nama` varchar(256) NOT NULL,
  `tanggal_lahir` date DEFAULT NULL,
  `jenis_kelamin` varchar(2) DEFAULT NULL COMMENT 'LK/PR',
  `nomor_telepon` varchar(64) DEFAULT NULL,
  `alamat` text DEFAULT NULL,
  `waktu_daftar_user` datetime NOT NULL DEFAULT current_timestamp(),
  `waktu_terakhir_ganti_password` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `user`
--

INSERT INTO `user` (`id_user`, `email`, `password`, `nama`, `tanggal_lahir`, `jenis_kelamin`, `nomor_telepon`, `alamat`, `waktu_daftar_user`, `waktu_terakhir_ganti_password`) VALUES
(1, 'tes@gmail.com', '7a8a80e50f6ff558f552079cefe2715d', 'satrio', '2002-05-08', 'LK', '082282741480', 'lampung', '2023-07-19 20:42:40', '2023-07-20 11:24:43'),
(2, 'tes2@gmail.com', 'fa3fb6e0dccc657b57251c97db271b05', 'satrio', NULL, NULL, NULL, NULL, '2023-07-20 11:12:43', '2023-07-20 11:12:43'),
(3, 'tes3@gmail.com', 'fa3fb6e0dccc657b57251c97db271b05', 'satrio', NULL, NULL, NULL, NULL, '2023-07-20 11:13:05', '2023-07-20 11:13:05'),
(4, 'tes4@gmail.com', 'fa3fb6e0dccc657b57251c97db271b05', 'satrio', NULL, NULL, NULL, NULL, '2023-07-20 11:24:51', '2023-07-20 11:24:51');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `divisi`
--
ALTER TABLE `divisi`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `pegawai`
--
ALTER TABLE `pegawai`
  ADD PRIMARY KEY (`nomor_pegawai`),
  ADD KEY `pegawai_ibfk_1` (`id_divisi`);

--
-- Indeks untuk tabel `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_user`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `divisi`
--
ALTER TABLE `divisi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `pegawai`
--
ALTER TABLE `pegawai`
  MODIFY `nomor_pegawai` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT untuk tabel `user`
--
ALTER TABLE `user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `pegawai`
--
ALTER TABLE `pegawai`
  ADD CONSTRAINT `pegawai_ibfk_1` FOREIGN KEY (`id_divisi`) REFERENCES `divisi` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
