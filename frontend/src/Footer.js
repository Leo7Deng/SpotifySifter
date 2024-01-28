import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

function Footer() {
    return (
        <>
            <hr className='bar'></hr>
            <div className="home-footer">
                <p className="footer-text">Created by Leo Deng</p>
                <p className="footer-text">© 2024 - SpotifySifter.com</p>
                <div className="footer-links">
                    <Link className="link" to="/">Home </Link> |
                    <Link className="link" to="/about"> About </Link> |
                    <Link className="link" to="/contact"> Contact</Link>
                </div>
            </div>
        </>
    );
}

export default Footer;